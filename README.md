# Combined Workflow
This is a demonstration package using
[mozbitbar](https://github.com/worldomonation/mozbitbar) and
[testdroid-api)(https://github.com/bitbar/testdroid-api).

# Requirements Installation

It is recommended that a Python virtual environment be used to install
the packages in the requirements.txt file.

# Download mozilla-bitbar-docker

Clone https://github.com/bclary/mozilla-bitbar-docker into a location
on your system and note the path.

# Download Testdroid.apk

Download
https://github.com/bitbar/bitbar-samples/blob/master/apps/builds/Testdroid.apk
into a location on your system and note the path.

# Execute the recipe to create the mozilla test image at Bitbar

``` bash
python create-mozilla-bitbar-image.py  \
    --mozilla-bitbar-docker-dir <path-to-mozilla-bitbar-docker> \
    --testdroid-apk <path-to-Testdroid.apk> \
	--recipe workflow.yaml
```
