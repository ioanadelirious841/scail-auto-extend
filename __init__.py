"""SCAIL Auto Extend — single node that generates a full-length SCAIL-2 video
by looping chunks internally (81 frames, then 76-new/5-overlap extensions),
replacing the manually-bypassed extension sections of the SCAIL Extend workflow.

Wraps the core WanSCAILToVideo / SamplerCustom / ColorTransfer node logic.
"""

import math

import torch

import comfy.model_management
import comfy.utils


def _plan_chunks(n_frames, chunk_len, overlap):
    """Trim n_frames to 4n+1, return list of chunk lengths (all 4n+1).
    Coverage = lengths[0] + sum(L - overlap for L in lengths[1:]) == n_eff."""
    n_eff = ((n_frames - 1) // 4) * 4 + 1
    if n_eff <= chunk_len:
        return n_eff, [n_eff]
    step = chunk_len - overlap
    k = math.ceil((n_eff - chunk_len) / step)
    final_len = n_eff - step * k
    return n_eff, [chunk_len] * k + [final_len]


class SCAILAutoExtend:
    DESCRIPTION = (
        "Generates the full video in one go: samples the first chunk, then "
        "automatically loops as many extension chunks as the pose video needs, "
        "anchoring each on the last frames of the previous chunk, and stitches "
        "the result. Replaces the manual extension sections."
    )
    CATEGORY = "sampling/video"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "frame_count")
    FUNCTION = "generate"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "vae": ("VAE",),
                "sampler": ("SAMPLER",),
                "sigmas": ("SIGMAS",),
                "pose_video": ("IMAGE",),
                "width": ("INT", {"default": 512, "min": 32, "max": 8192, "step": 32}),
                "height": ("INT", {"default": 896, "min": 32, "max": 8192, "step": 32}),
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                                       "control_after_generate": True}),
                "cfg": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "chunk_length": ("INT", {"default": 81, "min": 9, "max": 1024, "step": 4,
                                         "tooltip": "Max frames per chunk (model limit 81). Must be 4n+1."}),
                "overlap": ("INT", {"default": 5, "min": 1, "max": 81, "step": 4,
                                    "tooltip": "Frames from the previous chunk used as anchor. SCAIL-2 trained at 5."}),
                "seed_mode": (["increment", "fixed"], {"default": "increment",
                              "tooltip": "increment: chunk i uses noise_seed+i. fixed: same seed every chunk."}),
                "color_transfer": ("BOOLEAN", {"default": True,
                                   "tooltip": "Reinhard LAB color match of each extension chunk to the last frame of the previous chunk (fights drift)."}),
            },
            "optional": {
                "pose_video_mask": ("IMAGE",),
                "reference_image": ("IMAGE",),
                "reference_image_mask": ("IMAGE",),
                "clip_vision_output": ("CLIP_VISION_OUTPUT",),
                "replacement_mode": ("BOOLEAN", {"default": True}),
                "pose_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "pose_start": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "pose_end": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "add_noise": ("BOOLEAN", {"default": True}),
            },
        }

    def generate(self, model, positive, negative, vae, sampler, sigmas, pose_video,
                 width, height, noise_seed, cfg, chunk_length, overlap, seed_mode,
                 color_transfer, pose_video_mask=None, reference_image=None,
                 reference_image_mask=None, clip_vision_output=None,
                 replacement_mode=True, pose_strength=1.0, pose_start=0.0,
                 pose_end=1.0, add_noise=True):
        # imported here so a missing/changed core module gives a clear error at run time
        from comfy_extras.nodes_scail import WanSCAILToVideo
        from comfy_extras.nodes_custom_sampler import SamplerCustom
        from comfy_extras.nodes_post_processing import ColorTransfer

        chunk_length = ((chunk_length - 1) // 4) * 4 + 1
        if overlap % 4 != 1:
            overlap = max(1, ((overlap - 1) // 4) * 4 + 1)
        if chunk_length - overlap < 4:
            raise ValueError(f"chunk_length ({chunk_length}) must exceed overlap "
                             f"({overlap}) by at least 4.")

        n_input = pose_video.shape[0]
        n_eff, lengths = _plan_chunks(n_input, chunk_length, overlap)
        print(f"[SCAIL Auto Extend] {n_input} pose frames -> {n_eff} output frames, "
              f"{len(lengths)} chunk(s): {lengths}")

        pbar = comfy.utils.ProgressBar(len(lengths))
        chunks = []          # stitched contributions
        prev_frames = None   # full frames of previous chunk's contribution
        offset = 0

        for i, length in enumerate(lengths):
            comfy.model_management.throw_exception_if_processing_interrupted()
            seed = noise_seed + i if seed_mode == "increment" else noise_seed

            cond = WanSCAILToVideo.execute(
                positive=positive, negative=negative, vae=vae,
                width=width, height=height, length=length, batch_size=1,
                pose_strength=pose_strength, pose_start=pose_start, pose_end=pose_end,
                video_frame_offset=offset, previous_frame_count=overlap,
                replacement_mode=replacement_mode,
                reference_image=reference_image,
                clip_vision_output=clip_vision_output,
                pose_video=pose_video, pose_video_mask=pose_video_mask,
                reference_image_mask=reference_image_mask,
                previous_frames=prev_frames,
            )
            pos_c, neg_c, latent, offset = cond.args

            sampled = SamplerCustom.execute(
                model=model, add_noise=add_noise, noise_seed=seed, cfg=cfg,
                positive=pos_c, negative=neg_c, sampler=sampler, sigmas=sigmas,
                latent_image=latent,
            )
            denoised = sampled.args[1]  # denoised_output

            images = vae.decode(denoised["samples"])
            if images.ndim == 5:
                images = images.reshape(-1, *images.shape[-3:])

            if i == 0:
                contrib = images
            else:
                contrib = images[overlap:]
                if color_transfer and prev_frames is not None:
                    contrib = ColorTransfer.execute(
                        image_target=contrib,
                        image_ref=prev_frames[-1:],
                        method="reinhard_lab",
                        source_stats={"source_stats": "per_frame"},
                        strength=1.0,
                    ).args[0]

            chunks.append(contrib)
            prev_frames = contrib
            pbar.update(1)
            print(f"[SCAIL Auto Extend] chunk {i + 1}/{len(lengths)} done "
                  f"({length} frames, offset now {offset})")

        out = torch.cat([c.to(chunks[0].device, dtype=chunks[0].dtype) for c in chunks], dim=0)
        return (out, out.shape[0])


NODE_CLASS_MAPPINGS = {"SCAILAutoExtend": SCAILAutoExtend}
NODE_DISPLAY_NAME_MAPPINGS = {"SCAILAutoExtend": "SCAIL Auto Extend Sampler"}
