
# cttfind4

The `includes/myami/appion/bin/ctffind4.py` file states that:

```python
class ctfEstimateLoop(appionLoop2.AppionLoop):
	"""
	appion Loop function that
	CTFFIND 4 was written by Alexis Rohou.
	Appion is Compatible with CTFFIND version 4.1.5
	http://emg.nysbc.org/redmine/projects/appion/wiki/Package_executable_alias_name_in_Appion
	to estimate the CTF in images
	"""
...
```

so we downloaded:

https://grigoriefflab.umassmed.edu/system/tdf?path=ctffind-4.0.17-linux64.tar.gz&file=1&type=node&id=26

to:

`includes/ctffind-4.1.5-linux64`

in case The Grigorieff Lab site stops hosting the source. Then we add this material to the `Dockerfile` and symlink the binaries.
