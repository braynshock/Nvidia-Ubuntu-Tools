# Nvidia-Ubuntu-Tools
Some overclocking scripts that give a few more options than the nvidia-settings app has

## nvidia-fan-control.py
This script can be run in the background to monitor GPU temps, and adjust Fan speed accordingly.
 
#### Notes
- proof of concept script prior to C implementation
- editable configuration options (lines 9-20)
- works only with one GPU, and one Fan configuration option in GPU firmware
- many GPUs with multiple fans treat them as one in the firmware (true for both of mine)

#### Usage
set permission to 755 and execute
```python
chmod 755 ./nvidia-fan-control.py
./nvidia-fan-control.py
or
python3 nvidia-fan-control.py
```
