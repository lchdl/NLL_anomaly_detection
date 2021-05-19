# NLL_anomaly_detection
A simple anomaly detection algorithm for medical imaging based on multi-atlas image registration and negative log likelihood.

## Paper
MICCAI-2021: Improved Brain Lesion Segmentation with Anatomical Priors from Healthy Subjects.

## Prerequisites
You need to install the following softwares for running the code.

**ANTs-2.3** (older versions should also work) and **FSL-6.0**

If you already have **ANTs** and **FSL** installed before, just skip the following steps.

> **1. ANTs (Advanced Normalization Tools)**
>
> Link to ANTs: https://github.com/ANTsX/ANTs
>
> How to install: compile from [source code](https://github.com/ANTsX/ANTs) (recommended) or pre-built [binaries](https://github.com/ANTsX/ANTs/releases)
> 
> Verify your install: to see whether ANTs is installed correctly on your system, after the installation you need to type in
> ```
> antsRegistration --version
> ```
> in your console. It should produce output such as:
> ```
> ANTs Version: 3.0.0.0.dev13-ga16cc
> Compiled: Jan 22 2019 00:23:29
> ```

> **2. FSL (FMRIB Software Library)**
>
> Link to FSL: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki
>
> How to install: FSL is installed using the *fsl_installer.py* downloaded from [here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation). You need to register your personal information to the FSL site before download. After download you need to run the installer script and wait for the installation to finish.
>
> Verify your install: when the installation finished, type in
> ```
> bet -h
> ```
> in your console. If no error occurs then everything is OK :)

## Quick start



## Details of each step


