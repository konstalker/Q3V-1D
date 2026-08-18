from base_methods import *
import os

load_wait = "300"
demo_dir = "../baseq3/mods/osp/demos"
out_cfg = "../baseq3/mods/osp/batchconvert.cfg"

demos = sorted(f for f in os.listdir(demo_dir) if f.endswith(".dm_68"))

lines = []
for i, demo in enumerate(demos):
    name = os.path.splitext(demo)[0]
    step = f"step{i}"
    next_step = f"step{i+1}" if i + 1 < len(demos) else "final"

    lines.append(f'set {step} "stopvideo; demo {name}; wait {load_wait}; video-pipe; set nextdemo vstr {next_step}"')

lines.append('set final "stopvideo; quit"')
lines.append("vstr step0")

with open(out_cfg, "w") as f:
    f.write("\n".join(lines))

print(f"Готово: {out_cfg}, демок: {len(demos)}")

print('starting quake')
launch(args2="+exec video.cfg +exec batchconvert.cfg")
