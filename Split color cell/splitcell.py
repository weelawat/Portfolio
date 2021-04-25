from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import cv2
import numpy as np
import glob
import os
import xlsxwriter

def inputpf():
    #Input patch file
    pf = input("Drag folder here or Enter patch file:") 
    pf = pf.replace("\\", "") 
    if pf[-1] == " ":
        pf = pf[:-1]
    return pf

def markim(pf):
    #List tiff file
    patchfile = glob.glob(pf + "/" + "*.tiff")

    #Create Save Dir
    savedir = (pf + "/" + "Marked")
    try:
        os.mkdir(savedir)
    except OSError:
        pass

    #Create excel file
    workbook = xlsxwriter.Workbook(savedir + "/" + "Workbook.xlsx")

    for impatch in patchfile:
    
        #Create woork sheet
        worksheet = workbook.add_worksheet(impatch.split("/")[-1][:-5])
        worksheet.write(0, 0, "Cell No.")
        worksheet.write(0, 1, "Area")
        worksheet.write(0, 2, "Mean")
        worksheet.write(0, 3, "IntDen")
    
        #Import image
        im = Image.open(impatch)

        #Set to array
        imarray = np.array(im)

        #Delete R B color
        gimarray = imarray.copy()
        gimarray[:, :, 0] = 0
        gimarray[:, :, 2] = 0

        #Split G color array
        gchimarray = gimarray[:, :, 1] #G chanel array ==> gray color
        cv_gchimarray = gchimarray.copy() #Bufer for opencv process
        cv_gchimarray[cv_gchimarray < 30] = 0 #Fillter noise
        cv_gchimarray[cv_gchimarray > 0] = 100 #Set to plain gray scale

        #Find&Draw contour
        _, contours, _ = cv2.findContours(cv_gchimarray, 
                                          cv2.RETR_EXTERNAL, 
                                          cv2.CHAIN_APPROX_SIMPLE)
 
        i = 1
        for c in contours:
       
            cntarea = cv2.contourArea(c)
    
            if cntarea > 500 and 1023 not in c and 0 not in c: #Improve logic!!!
        
                #Check centroid of contours
                M = cv2.moments(c)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                #Create hull
                hull = cv2.convexHull(c)
        
                #Calculate Mean, IntDen
                mask = np.zeros(cv_gchimarray.shape, np.uint8)
                cv2.drawContours(mask, [hull], 0, 255, -1)
                mean_val = cv2.mean(gimarray, mask=mask)[1]
                #print(i, cntarea, round(mean_val/3, 2), round(mean_val*cntarea/3, 2))
            
                #Write to excel file
                worksheet.write(i, 0, i)
                worksheet.write(i, 1, cntarea)
                worksheet.write(i, 2, round(mean_val/3, 2))
                worksheet.write(i, 3, round(mean_val*cntarea/3, 2))
        
                #Draw Hull, Number
                cv2.drawContours(gimarray, [hull], 0, (0, 0, 255), 2)
                cv2.putText(gimarray, str(i), (cX - 10, cY), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
                i = i + 1

        #combine 2 image
        imarray = np.concatenate((imarray, np.full((1024, 2, 3), 255, dtype="uint8"), gimarray), axis=1)
      
        #Save image
        Finalim = Image.fromarray(imarray)
        Finalim.save(savedir + "/Marked_" + impatch.split("/")[-1][:-5] + ".jpg")
    
    workbook.close()
    pf = ""
    print("Done!!!\n")
    Image.fromarray(gimarray)

while True:   
    try:
        pf = inputpf()
        if os.path.exists(pf):
            markim(pf)
    except:
        pass
