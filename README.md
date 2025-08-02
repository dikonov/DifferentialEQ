# DifferentialEQ

Create nicely averaged EQ curves to match equalization between different audio sources.

## Overview
When dealing with audience recordings or ROIOs in general, we are often confronted with wonky equalization. This can have a number of reasons such as bad recording equipment (nonlinear microphone response) or multiple analog tape generations (misaligned azimuth, noise, tape speed/resolution). Commercial software such as Izotope RX allows us to match the equalization of a muffled source to a reference recording using a method called 'differential equalization'. That works well for individual recordings, but what if we want to process entire concerts in this way? Usually, you won't have a reference for every source song and you also don't want your equalization to change too much between tracks. This is where the power of averaging comes in, brought to you by this free tool to be used with audacity.

With this tool, you can sample any number of source > reference pairs. The resulting differential EQ curves are averaged into one output EQ curve that you can then use to process all your sources. The averaging process cancels out local inaccuracies and reinforces the global trend of your recording's EQ problems. The resulting averaged EQ curve should thus allow you to restore the recording to an ideal equalization when you apply it in audacity.

## Installation
- Install Python 3.6
- Open the command line (with admin rights). Type `pip install numpy pyqt5 matplotlib pysoundfile`
- Click the `Clone or Download` button at the right, then `Download ZIP`. Unzip to a folder of your choice.

![Imgur](https://i.imgur.com/Wei3V43.png)

## How to Use
- Shift+Rightclick in the folder with the scripts and run the windows power shell / command line. Type `python difeq.py` and enter.
- "+" Add a new differential EQ (opens file dialogs to select source and reference file)
- "-" Delete the selected EQ from the list.
- "=" Export the current average EQ to an XML file for use in Audacity.
- The top two numbers fade in the influence of the EQ curve over the given frequencies to avoid boosting the bass or LF noises. Consider this the start and end of your EQ curve's 'rollon' band.
- The next two numbers fade out the influence of the EQ curve over the given frequencies to avoid boosting the noise floor. Consider this the start and end of your EQ curve's 'rolloff' band.
- The bottom four numbers control the resolution, smoothing, gain and volume shift of the curve.
- Select which channels you want to compare for stereo files.
- nb. See also the tooltips that appear when you keep your mouse over a button.

## Detailed Hints
### Averaging and Smoothing
The general idea is that you use several different pairs of source and reference files. For audience tape restoration, you could take each of the songs as source and map to official versions, respectively. See the list in the screenshot - several curves are used to determine the final output. The more curves you have, the more accurate the result (in theory). If you have obvious outliers, you can delete their curves.
When you have less pairs of samples available, you might want to increase the smoothing that is applied to the averaged curve. On the other hand, if you have a big sample size, you can increase the resolution of the output curve and reduce the smoothing factor to get a more detailed EQ curve.

### Rolloff
Essentially, both numbers specify the "rolloff" of the EQ curve, but you can think of it in two perspectives, so to speak

From a source material point of view:
- top number: at this freq there is still clean signal on the aud source, check in the audacity spectral view (NOT in `Plot Spectrum`, that is ambiguous because you can't safely discern low clean signal from loud noise in the plotted graph). Click the track name dropdown menu, and then select `Spectrogram`, then scroll into the region of interest.
- bottom number: at this freq there is no more music signal on your source, only uniform noise

From the final EQ curve point of view:
- top number: at this freq the differential EQ is fully in effect, ie. this freq may be boosted or lowered in any way according to the diff EQ sources in your list
- bottom number: at this freq, the calculated diff EQ is faded to zero influence, ie. the original source is left untouched above this frequency
Now the default setting simply means the diff EQ is fully in effect up to 21000Hz, then fades to zero influence at 22000Hz and has no influence above. No matter how you set the numbers, you can not "destroy" / "cut off" audio with them, as anything above the second number remains "untouched". The sampling rate of the material does not really matter for this, no need to worry about that.

So how to set them?
If you set them too high/keep the defaults, you boost noise on these audience recordings.
If you set them too low, you don't amplify some of the good signal.

### Muddiness
If you are using the tool properly, the fat blue line should become smoother as you add more differential EQs to the list. This smoothness does not equal muddiness. Remember, the fat blue line is NOT the final spectrum of every source recording, but the DIFFERENCE that should be added to each spectrum via EQ to restore its sound.

### Shrillness
Something is usually perceived as too shrill when there is too much energy in the high frequency range. This can have two reasons:
- Either, the EQ is more or less fine objectively speaking, but there is distortion and that sounds shriller than proper signal at the same volume. This is often the case with audience recordings, so you have to be careful with the differential EQs... It all boils down to how clean the source was. Note that a harmonic-percussive separation algorithm can improve the results.
- Or, the EQ is simply too strong for the high frequencies, even though they are clean and free of distortion. You should not be getting this after properly applying differential EQ.

### Stereo Channel Selection
L+R analyzes both channels for source and reference, so you get an averaged result for both channels, as if they were mono.
L only analyzes the L channels for source and reference, and R does the same, respectively.
Consider practical use cases:
- you have a mono audience recording, which needs to be cleaned up, and have stereo official references: use "L+R" to capture the average of the official mix to compare with your mono
- you have a stereo audience or multi-gen soundboard with THE SAME EQ ISSUES ON BOTH CHANNELS, as well as stereo references: use "L+R"  to compare the folddown of both
- you have a stereo audience or multi-gen soundboard with DIFFERENT EQ ISSUES ON EITHER CHANNEL, as well as stereo references: use "L", create your EQ curve, process left channel in audacity with L EQ curve. Then delete all curves and switch to "R", load the same files again and use the R EQ curve on the right channel. [in an upcoming version, maybe this could be simplified, so you don't have to do essentially the same work of twice]
