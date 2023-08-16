# CemrgApp Scar Quantification for Batch Processing
Run CemrgApp scar quantification quickly on a batch process. 

> Only supports CemrgApp v2.2.

## Usage 
Create `segmentation.vtk` from a segmentation file: 
```shell
python process.py surf --base-dir [PATH/TO/DATA] --segmentation [SEGMENTATION_NAME.nii] 
```

Create a scar map from an LGE image: 
```shell
python process.py surf --base-dir [PATH/TO/DATA] --scar-lge [LGE_NAME.nii] --scar-measurements {iir, msd} --scar-sweep {thresholds}
```

the `{thresholds}` in option `--scar-sweep` can be one of the following: 
+ Individual, for example: `0.97`
+ Comma-separated, for example: `0.97,1.2,1.32`
+ Sweeps following a `FIRST:INCREMENT:LAST` format, for example `0.97:0.01:1.32`
> "All values between 0.97 and 1.32 with increments of 0.01"

Show help
```shell
python process.py -h
```
