# LipReading
This scripts generates a descriptor of mouth movement during syllable articulation. 

We extract key frames by comparing pixel intensity histogram correlations. The first key frame  and baseline frame is frame 0.  Following pixel intensity histogram are extracted to calculate their correlation coefficient between itself and the baseline frame.If the correlation treshold es greater than the correlation coefficient, such frame is saved as both keyframe and baseline frame.

Face (Viola and Jones, 2001), and 68 facial landmarks (Kazemi and Sullivan, 2014)
are detected at the same time as the aforementioned. From facial landmarks we locate mouth as  a ROI (Region Of Interest) of 20 landmarks. A vector of the movement of each landmark is extracted between keyframes. From such vector we calculate an eight bins Oriented Histogram of Regional Optical Flow (Liu et al., 2016), a total of 20  of such histograms are computed and joined as a 160 dimensional vector. A vector containing each mouthlandrk mean histogram values is calculated by the end of the video, such vector is our final descriptor
