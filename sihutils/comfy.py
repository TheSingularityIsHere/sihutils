import json
import os
import subprocess

import ipywidgets
import IPython.display
import tqdm.notebook


def _runcmd(cmd, env):
  process = subprocess.Popen(
    cmd,
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
  )

  progress_area = ipywidgets.Output()
  IPython.display.display(progress_area)

  for line in process.stdout:
    if "━" in line:
      with progress_area:
        progress_area.clear_output(wait=True)
        print(line, end="")
    else:
      # Regular logs outside the 'with' block print to the main cell
      print(line, end="")

  process.wait()


def render_script(
  # https://github.com/TheSingularityIsHere/human-in-the-loop/blob/main/script_writer/script_writer.py
  script_path='20260331_205938.json',
  scene0=0,
  scene1=None,
  dest='/workspace/runpod-slim/ComfyUI/output/video'
):

  env = {**os.environ}
  env["COMFYUI_PROMPT_ACK"] = "true"

  name = os.path.splitext(os.path.basename(script_path))[0]
  script = json.load(open(script_path))
  if scene1 is None:
    scene1 = len(script['scenes'])

  for scene_i in tqdm.notebook.trange(scene0, scene1):

    prompt = script['scenes'][scene_i]['writer']['text']
    frames_number = 25 * 20

    os.makedirs(dest, exist_ok=True)

    wf_path = os.path.join(
      os.path.dirname(__file__),
      # download "File / Export (API)"
      'video_ltx2_3_t2v_api.json',
    )
    wf_name = os.path.splitext(os.path.basename(wf_path))[0]
    wf = json.load(open(wf_path))

    wf['267:266']['inputs']['value'] = prompt
    wf['267:225']['inputs']['value'] = frames_number

    dest_wf_path = os.path.join(dest, f'{name}__scene{scene_i:05}__{wf_name}.json')
    with open(dest_wf_path, 'w') as f:
        json.dump(wf, f)

    cmd = ["comfy", "run", "--wait", "--timeout=3600", f"--workflow={dest_wf_path}"]
    _runcmd(cmd, env)
