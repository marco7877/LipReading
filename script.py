#!/usr/bin/env python3
# -*- coding: utf-8 -*-

######
#
# Marco A. Flores-Coronado, Universidad Autónoma del Estado de Morelos (UAEM)
# 2020
#
# This code analizes video information. It requires opencv 3, Dlib, 
# a haarscascade pretrained model, and a ensemble regresion tree to detect 
# human faces and to extract their features (position of mouth, eyes, etc.)
# The script works as follows:
# -it analizes videos from peaople saying syllables
# - extract key frames from video by an aspect criteria 
# (grayscale histograms from each frame)
# -when key frames are selected, it computes the direction and magnitude of every 
# point ihe ROI from key frame t to t+1, the saves such result in a histogram
# -all resulting histograms for each point inside the ROI are summed and normalized
#
####Neither the haars cascade nor the shape predictor models are from my authorship
#
#The haars cascade model, and their corresponding license, can be downloaded from de OpenCV git page
# (https://github.com/opencv/opencv/tree/master/data/haarcascades).
#
#Shape predictor can be downloaded from:
# https://osdn.net/projects/sfnet_dclib/downloads/dlib/v18.10/shape_predictor_68_face_landmarks.dat.bz2/
#
#NOTES:
#outter lips indexes: 48:61
#inner lips indexes: 61:68

##### libraries ##################
import cv2 as cv
import numpy as np
import dlib
import matplotlib.pyplot as plt
import math

cascade='./haarcascade_frontalface_default.xml'
model= './shape_predictor_68_face_landmarks.dat'
##### functions#############
def list_p(objeto):
    variable=([])
    for p in objeto:
        temporal=[p.x,p.y]
        variable.append(temporal)
    return variable
def unarrange(listofarray):
    mylist=[]
    for  i in range(len(listofarray)):
        for j in range(len(listofarray[0])):
            array=listofarray[i]
            element=array[j]
            mylist.append(element)
    return mylist
def eucl (coord1,coord2):
    n1=np.array(coord1)
    n2=np.array(coord2)
    eud=np.linalg.norm(n1-n2)
    return eud
def splitlist(mylist,nlist):
    sublists=[mylist[x:x+nlist] for x in range(0,len(mylist),nlist)]
    return sublists
def descriptorhist(coordlist1,coordlist2,vectorlist):
    list1=splitlist(coordlist1,2)
    list2=splitlist(coordlist2,2)
    distances=[]
    for coord in range(len(list1)):
        euclidean=eucl(list1[coord],list2[coord])
        distances.append(euclidean)
    tempvec=[]
    for i in range(len(vectorlist)):
        coordif=vectorlist[i]
        tempvec.append(math.atan2(coordif[0],coordif[1]))
        angledummy=[]
    for x in range(len(tempvec)):
        isangle=math.degrees(tempvec[x])
        if isangle<0:
            isangle=isangle+360
        angledummy.append(isangle)
    datota=[]
    for j in range(len(angledummy)):
        myhistogram=np.histogram(angledummy[j],bins=8,range=(0,360))
        data=myhistogram[0]
        datota.append(data)
    for i in range(len(distances)):
        datota[i]=datota[i]*distances[i]
    return datota
            
def selection(mini,maxi,objec):
    hh=[]
    for i in range(mini,maxi):
        temporal=objec[i]
        hh.append(temporal)
    return hh
def axis(array):
    x=[]
    y=[]
    for i in range(len(array)):
        w,z=np.split(array[i],2)
        x.append(w)
        y.append(z)
    return x,y
def areas(array1,array2,integrers):
    amount=len(array1)
    new1=[]
    new2=[]
    for i in range(amount):
        n1=array1[i]+integrers
        n2=array2[i]+integrers
        new1.append(n1)
        new2.append(n2)
    return new1, new2

def area_roi(x_axis,y_axis2,image):
    mini=np.amax(x_axis)
    miniy=np.amin(y_axis2)
    maxiy=np.amax(y_axis2)
    roi=image[int(mini):245,miniy:maxiy]
    return roi
def mouth_roi(x_axis,y_axis,image):
    mn1=np.amin(x_axis)
    mx1=np.amax(x_axis)
    mn2=np.amin(y_axis)
    mx2=np.amax(y_axis)
    roi=image[int(mn2):int(mx2),int(mn1):int(mx1)]
    return roi

def hist_norm(histogram):
    maxi=histogram.max()
    mini=histogram.min()
    normalization=(histogram-mini)/(maxi-mini)
    return normalization
def magnitudnorm(mylist):
    maximum=max(mylist)
    minimum=min(mylist)
    normalization=(mylist-minimum)/(maximum-minimum)
    return normalization
#esto genera una lista secvuencial de listas donde cada sublista 
#tiene nlist de my list
def CosSim(a,b):
    dotp=np.dot(a,b)
    lenga=np.linalg.norm(a)
    lengb=np.linalg.norm(b)
    cos=dotp/(lenga*lengb) ####### Esto es lo mismo que 
    #cos=np.dot(a,b)/((np.linalg.norm(a))*(np.linalg.norm(b)))
    return cos
############### main#############
recognizer= cv.CascadeClassifier(cascade)# <- este utiliza OPENCV
aligner=dlib.shape_predictor(model) # <- este utiliza DLIB
element="da8"
file="/media/marco/MarcoHDD/github/stimuli/"+ str(element)+".mp4"
KeyFrameInfo=[]
documentofinal="HistogramaDireccionMagnitud"+element+"Paper.txt"
cap=cv.VideoCapture (file)
forgevideo=True
playvideo=True
savetxt=True
readvideo=True
############
# reproducción y análisis de los videos: identificación rostro, identificación
# zonas de la boca, generación de nueva imagen de 8x8x20 px (8x8=recuadro boca)
# finalmente saca el descriptor hog con cell=8X8 y blocks= 8X16. 
# Descriptor hog por cuaef areas(array1,array2,integrers):
############
cuadro=1
keyframe=[]
KeyFrameInfo=[]
if forgevideo==True:
    vid_cod = cv.VideoWriter_fourcc(*'DIVX')
    output = cv.VideoWriter("video.avi", vid_cod, 20, (480,640))
while readvideo==True:
    ret, frame= cap.read()
    #print(frame.shape)
    #vid_cod = cv.VideoWriter_fourcc(*'XVID')
    if ret==False:
        print("Can't get frames from video, RET== False in frame #"+str(cuadro))
        break   
    gray=cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces=recognizer.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=5,
        minSize=(200,200),# minimum dimensions of face in pixels
        flags=cv.CASCADE_SCALE_IMAGE)
    for (x,y,z,w) in faces:
        roi_gray=gray[y:y+w,x:x+z]
        end_coord_x=x+z
        end_coord_y=y+w
        color=(255,0,0)
        stroke=4
        cv.rectangle(gray,(x,y),(end_coord_x,end_coord_y),color,stroke)
        dlib_face=dlib.rectangle(int(x),int(y),int(x+z),int(y+w))
        detected_landmarks=aligner(gray,dlib_face).parts()# landmarks coordinates
        landmarks=np.array(list_p(detected_landmarks))
        minimum=48
        maximum=68
        seleccion=selection(minimum,maximum,landmarks)
        mouthlandmarks_P=list(seleccion)
        for landmark in mouthlandmarks_P:
            x=landmark[0]
            y=landmark[1]
            cv.circle(gray, (x, y), 2, (250), -1)
        copy=gray*0
        for idx, point in enumerate(seleccion):
            pos=(point[0],point[1])
            copy[pos[0]][pos[1]]=300
            cv.circle(frame,pos,1,color)

        x_axis,y_axis=axis(seleccion)
        mouth=mouth_roi(x_axis,y_axis,frame)
        mouth2=mouth_roi(x_axis,y_axis,copy)
        histogram = cv.calcHist([mouth],[0],None,[256],[0,256]) # pixels intensity histogram
        histogram=np.resize(histogram,(256))
        histogram=hist_norm(histogram)
        seleccion_lst=[value for coordinate in seleccion for value in coordinate]
        my_coord_magnitudes=[]
        if forgevideo==True:
            gray4saving=cv.cvtColor(gray,cv.COLOR_GRAY2BGR)
            output.write(gray4saving)
        if playvideo==True:
            cv.imshow('Frame',gray)   
        if cuadro==1:
            plt.imshow(mouth2)
            plt.tight_layout()
            plt.show()
            keyframe=1
            temporal=histogram
            temporal_coord=seleccion_lst
        else:
            comparation=cv.compareHist(temporal,histogram,0)
            print(comparation)
            #comparation=.5
            if comparation>=0.5 and comparation<=0.71 and keyframe==1:
                plt.imshow(mouth2, cmap="autumn")
                plt.tight_layout()
                plt.show()
                temporal=histogram
                my_temp=[]
                for i in range(len(seleccion_lst)):
                    my_temp.append(seleccion_lst[i]-temporal_coord[i])
                KeyFrameInfo.append(my_temp)
                KeyFrameSum=my_temp
                vectorlist=splitlist(my_temp,2)
                descriptordummy=descriptorhist(temporal_coord,seleccion_lst,vectorlist)
                ###upper lines from else untill here computes magnitude and orientation histograms###
                temporal_coord=seleccion_lst
                keyframe+=1
                sumdescriptordummy=descriptordummy
            elif comparation>=0.5 and comparation<=0.71 and keyframe>1:
                plt.imshow(mouth2,cmap="autumn")
                plt.tight_layout()
                plt.show()
                temporal=histogram
                my_temp=[]
                for i in range(len(seleccion_lst)):
                    my_temp.append(seleccion_lst[i]-temporal_coord[i])
                for i in range(len(my_temp)):
                    KeyFrameSum[i]=KeyFrameSum[i]+my_temp[i]
                KeyFrameInfo.append(my_temp)
                vectorlist=splitlist(my_temp,2)
                descriptordummy=descriptorhist(temporal_coord,seleccion_lst,vectorlist)
                ###upper lines from elif untill here computes magnitude and orientation histograms###
                temporal_coord=seleccion_lst
                keyframe=keyframe+1
                for i in range(len(sumdescriptordummy)):
                    sumdescriptordummy[i]=sumdescriptordummy[i]+descriptordummy[i]
                temporal_coord=seleccion_lst
                keyframe=keyframe+1
        cuadro=cuadro+1
     
    if cv.waitKey(24) & 0xFF == ord('q'):
        break
cap.release()
if forgevideo==True:
    output.release()
cv.destroyAllWindows()
if keyframe !=1:
    sumdescriptordummy=unarrange(sumdescriptordummy)
    sumdescriptordummy=magnitudnorm(sumdescriptordummy)
else:
    sumdescriptordummy=[0]*(160)
    print("Keyframes < 2, histogram will be filled with 0s")

if savetxt==True:
    print("saving descriptor as .txt in "+documentofinal)
    np.savetxt(documentofinal,sumdescriptordummy,fmt='%1.10f',delimiter=",")

#KeyFrameSum=np.array(KeyFrameSum)
#KeyFrameSum=np.reshape(KeyFrameSum,(1,40))
#plt.plot(KeyFrameSum)
#plt.title('Descriptor (Ga#3)')
#plt.show()

