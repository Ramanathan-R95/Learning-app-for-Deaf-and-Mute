from tkinter import *
import os
import random
from PIL import Image,ImageTk
import cv2
import pyttsx3
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time
from tkinter import messagebox



def textToSpeech(string):
        
    engine = pyttsx3.init()
    engine.setProperty("rate",140)
    #string = text.cget("text")
    engine.say(string)
    engine.runAndWait()


def predict(img,frame=None):
       
    hands,image=detector.findHands(img)
    try:
        if hands:
            if len(hands) == 1:
                # -------- Single Hand (Original Behavior) --------
                hand = hands[0]
                x, y, w, h = hand['bbox']
                imgCrp = img[y-22:y+h+22, x-22:x+w+22]
                imgWhite = np.ones((300, 300, 3), np.uint8) * 255

                ratio = h / w 
                if ratio > 1:
                    k = 300 / h
                    wcal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrp, (wcal, 300))
                    wgap = math.ceil((300 - wcal) / 2)
                    imgWhite[:, wgap:wgap+wcal] = imgResize
                else:
                    k = 300 / w
                    hcal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrp, (300, hcal))
                    hgap = math.ceil((300 - hcal) / 2)
                    imgWhite[hgap:hgap+hcal, :] = imgResize

            else:
                # -------- Two Hands (Side-by-Side Smaller) --------
                imgWhite = np.ones((300, 300, 3), np.uint8) * 255
                hand_images = []

                for hand in hands:
                    x, y, w, h = hand['bbox']
                    imgCrp = img[y-22:y+h+22, x-22:x+w+22]

                    ratio = h / w
                    if ratio > 1:
                        k = 140 / h
                        wcal = math.ceil(k * w)
                        imgResize = cv2.resize(imgCrp, (wcal, 140))
                        wgap = math.ceil((140 - wcal) / 2)
                        whiteHand = np.ones((140, 140, 3), np.uint8) * 255
                        whiteHand[:, wgap:wgap+wcal] = imgResize
                    else:
                        k = 140 / w
                        hcal = math.ceil(k * h)
                        imgResize = cv2.resize(imgCrp, (140, hcal))
                        hgap = math.ceil((140 - hcal) / 2)
                        whiteHand = np.ones((140, 140, 3), np.uint8) * 255
                        whiteHand[hgap:hgap+hcal, :] = imgResize

                    hand_images.append(whiteHand)

                if len(hand_images) == 2:
                    imgWhite[80:220, 10:150] = hand_images[0]
                    imgWhite[80:220, 160:300] = hand_images[1]

            pred,ind=classifier.getPrediction(imgWhite);
            #print(ind)
            return ind
    except :
        if frame:
            messagebox.showinfo("warning","Dont move the hands out of the Frame")
        #print("Dont move the hands out of the frame")
    return -1
                




def learn():
    if signToTextCam:
        cap.release()

    
    def alphabets():
        global currentIndex
        phtFrame = Frame(mainScreen,height=1100,width=1400,bg="#800020")
        phtFrame.grid_propagate(False)
        phtFrame.grid(column=2,row=1)
        video=Label(phtFrame)
        text1=Label(phtFrame,font=("Comic Sans MS",26),text="Your Sign :",fg="white",bg="#800020")
        text1.place(x=600,y=520)
        text=Label(phtFrame,font=("Comic Sans MS",26),text="Cannot find hands",fg="white", bg="#800020")
        text.place(x=860,y=520)
        alphabetPaths=[]
        alphaFolder=r"images\alphabets"
        imagesAlpha=[]
        currentIndex=0
        for file in os.listdir(alphaFolder):
            alphabetPaths.append(os.path.join(alphaFolder,file))
        for path in alphabetPaths:
            a_image=Image.open(path).resize((400,400))
            imagesAlpha.append( ImageTk.PhotoImage( a_image))
        imgLabel=Label(phtFrame)
        imgLabel.place(x=60,y=80)
        alphaLabel=Label(phtFrame,font=("Comic Sans MS",22),text=chr(65+currentIndex),fg="#800020",bg="white")
        camera=True
        def audio(text):
            textToSpeech(text)
        def showImage():
            #global imgLabel
            imgLabel.config(image=imagesAlpha[currentIndex])
            imgLabel.image=image=imagesAlpha[currentIndex]
            alphaLabel.config(text="Current Alphabet : " +chr(65+currentIndex))
        def prev():
            global currentIndex
            if currentIndex > 0:
                currentIndex-=1
            else:
                currentIndex=len(imagesAlpha)-1
            showImage()
        
        def next():
            global currentIndex
            
            currentIndex=(currentIndex+1) % len(imagesAlpha)
            showImage()



        def cam():
            
            global cap
            global camera
            cap = cv2.VideoCapture(0) 
            camera= True
            video.place(x=530,y=10)
            def quitCam():
                global camera
                camera = False
                video.place_forget()
                button1.place_forget()
                cap.release()
            button1=Button(phtFrame,text="Turn Off",command=quitCam,font=("Times",21,"bold"),bg="white",fg="#800020")
            button1.place(x=300,y=610)
            
            def rec():
                if not camera:
                    return
                success,img=cap.read()
                if not success:
                    
                    return
                
                c=predict(img,phtFrame)
                if c is not None:
                    print(c)
                    txt=labels[c]
                    print(txt)
                    text.config(text=txt)
                else :
                    text.config(text="Cannot find hands")
                tkimg = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                tkimg = Image.fromarray(tkimg)
                imgtk = ImageTk.PhotoImage(image=tkimg)
                video.imgtk=imgtk
                video.configure(image=imgtk)
                video.after(5,rec)
               # 
                
                    #cv2.imshow("white",imgWhite)
                #cv2.imshow("Image1",img)
                
            rec()
        showImage()
        
        alphaLabel.place(x=50,y=20)
        button2=Button(phtFrame,text="Turn On Camera",command=cam,font=("Times",21,"bold"),bg="#ffffff",fg="#800020")
        button2.place(x=300,y=520)
        prevButton=Button(phtFrame,font=("Times",19,"bold"),text="Previous",fg="#800020",bg="#F0E7D5",command=prev)
        nextButton=Button(phtFrame,font=("Times",19,"bold"),text="Next",fg="#800020",bg="#F0E7D5",command=next)
        playButton=Button(phtFrame,font=("Times",19,"bold"),text="Audio",fg="#800020",bg="#F0E7D5",command=lambda :audio(chr(65+currentIndex)))
        playButton.place(x=50,y=700)
        prevButton.place(x=260,y=700)
        nextButton.place(x=510,y=700)
                


    def words():
        global currentIndex
        phtFrame = Frame(mainScreen,height=1100,width=1400,bg="#800020")
        phtFrame.grid_propagate(False)
        phtFrame.grid(column=2,row=1)
        video=Label(phtFrame)
        text1=Label(phtFrame,font=("Comic Sans MS",26),text="Your Sign :",fg="white",bg="#800020")
        text1.place(x=600,y=520)
        text=Label(phtFrame,font=("Comic Sans MS",26),text="Cannot find hands",fg="white", bg="#800020")
        text.place(x=860,y=520)
        wordPaths=[]
        words = "everyone food hello house let our share welcome".split()
        wordFolder=r"images\words"

        imagesWord=[]
        currentIndex=0
        for file in os.listdir(wordFolder):
            wordPaths.append(os.path.join(wordFolder,file))
        for path in wordPaths:
            a_image=Image.open(path).resize((400,400))
            imagesWord.append( ImageTk.PhotoImage( a_image))
        imgLabel=Label(phtFrame)
        imgLabel.place(x=60,y=80)
        wordLabel=Label(phtFrame,font=("Comic Sans MS",22),text=words[currentIndex],fg="#800020",bg="white")
        camera=True
        def showImage():
            #global imgLabel
            imgLabel.config(image=imagesWord[currentIndex])
            imgLabel.image=image=imagesWord[currentIndex]
            wordLabel.config(text="Current Word : " + words[currentIndex])
        def prev():
            global currentIndex
            if currentIndex > 0:
                currentIndex-=1
            else:
                currentIndex=len(imagesWord)-1
            showImage()
        
        def next():
            global currentIndex
            
            currentIndex=(currentIndex+1) % len(imagesWord)
            showImage()



        def cam():
            
            global cap
            global camera
            cap = cv2.VideoCapture(0) 
            camera= True
            video.place(x=530,y=10)
            def quitCam():
                global camera
                camera = False
                video.place_forget()
                button1.place_forget()
                cap.release()
            button1=Button(phtFrame,text="Turn Off",command=quitCam,font=("Times",21,"bold"),bg="white",fg="#800020")
            button1.place(x=300,y=610)
            
            def rec():
                if not camera:
                    return
                success,img=cap.read()
                if not success:
                    
                        
                    
                    return
                
                c=predict(img,phtFrame)
                if c is not None:
                    txt=labels[c]
                    text.config(text=txt)
                else :
                    text.config(text="Cannot find hands")
                tkimg = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                tkimg = Image.fromarray(tkimg)
                imgtk = ImageTk.PhotoImage(image=tkimg)
                video.imgtk=imgtk
                video.configure(image=imgtk)
                video.after(5,rec)
               # 
                
                    #cv2.imshow("white",imgWhite)
                #cv2.imshow("Image1",img)
                
            rec()
        showImage()
        
        wordLabel.place(x=50,y=20)
        button2=Button(phtFrame,text="Turn On Camera",command=cam,font=("Times",21,"bold"),bg="#ffffff",fg="#800020")
        button2.place(x=300,y=520)
        prevButton=Button(phtFrame,font=("Times",19,"bold"),text="Previous",fg="black",bg="white",command=prev)
        nextButton=Button(phtFrame,font=("Times",19,"bold"),text="Next",fg="black",bg="white",command=next)
        playButton=Button(phtFrame,font=("Times",19,"bold"),text="Audio",fg="#800020",bg="#F0E7D5",command=lambda :textToSpeech(words[currentIndex]))
        playButton.place(x=50,y=700)
        prevButton.place(x=260,y=700)
        nextButton.place(x=510,y=700)
        

    # def sentence():
    #     phtFrame = Frame(mainScreen,height=1100,width=1400,bg="white")
    #     phtFrame.grid_propagate(False)
    #     phtFrame.grid(column=2,row=1)

    learnFrame = Frame(mainScreen,height=1100,width=1400,bg="#800020")
    learnFrame.grid(column=2,row=1)
    learnFrame.grid_propagate(False)
    label=Label(learnFrame,text="What do you want to learn?",fg="white",bg="#800020",font=("Times",31,"bold"))
    label.place(x=160,y=155)
    label1=Label(learnFrame,text="Alphabets",fg="white",bg="#800020",font=("Times",30,"bold"))
    label2=Label(learnFrame,text="Words",fg="white",bg="#800020",font=("Times",30,"bold"))
    #label3=Label(learnFrame,text="Simple Sentence",fg="#2c3e50",bg="#800020",font=("Times",25))
    button2=Button(learnFrame,text="Click Here",bg="white",fg="#800020",font=("Times",21,"bold"),command=words)
    button1=Button(learnFrame,text="Click Here",bg="white",fg="#800020",font=("Times",21,"bold"),command=alphabets)
    #button3=Button(learnFrame,text="Click Here",bg="white",fg="#800020",font=("Times",21),command=sentence)
    
    button1.place(y=350,x=540)

    button2.place(y=440,x=540)
    #button3.place(y=330,x=440)
    label1.place(x=250,y=350)

    label2.place(x=250,y=440)
    #label3.place(x=150,y=330)
    





def signToText():
    def clearText():
        text.config(text="")
    

    
        


    global signToTextCam
    signToTextCam=True
    
    phtFrame = Frame(mainScreen,height=1100,width=1400,bg="#472830")
    
    heading=Label(phtFrame,text="Sign Language to Text/Speech",fg="#FFFCEF",bg="#472830",font=("Times",29,"bold"))
    heading.place(x=190,y=50)
    phtFrame.grid(column=2,row=1)
    phtFrame.grid_propagate(False)
    text1=Label(phtFrame,text="Your Text",fg="#FFFCEF",bg="#472830",font=("Times",29,"bold"))
    text1.place(x=100,y=650)
    text=Label(phtFrame,text="",fg="#FFFCEF",bg="#472830",font=("Times",29,"bold"))
    text.place(x=300,y=650)
    video = Label(phtFrame)
    phtFrame.focus_set()
    speechButton=Button(phtFrame,text="Clear Text",fg="#2c3e50",bg="white",font=("Times",21),command=clearText)
    resetButton=Button(phtFrame,text="Speech",fg="#2c3e50",bg="white",font=("Times",21),command=lambda:textToSpeech(text.cget("text")))
    speechButton.place(y=490,x=960)
    resetButton.place(y=550,x=960)
    textToSpeech("Hi, You can convert your sign language to speech in few seconds,..")
    
   # text = Label(phtFrame,font=("Times",20))
    

    
    def cam():
        global lastCapture
        global cap
        global camera
        try:
            lastCapture = time.time()
            cap = cv2.VideoCapture(0) 
            camera= True
            video.place(x=170,y=130)


            def rec():
                global lastCapture

                if not camera:
                    return
                success,img=cap.read()
                if not success:
                    
                    return
                currentCapture = time.time()
                if currentCapture - lastCapture> 3 :
                    hands,image=detector.findHands(img)
                    if hands:


                        c=predict(img,phtFrame)

                        text.config(text = text.cget("text")+labels[c])
                        lastCapture = currentCapture
                # if c is not None:
                #     txt=chr(c+65)
                # text.config(text=txt)
                # phtFrame.bind("<Key>",lambda event :onKeyPress(event,text,txt) )
                # else :
                #     text.config(text="Cannot find hands")
                tkimg = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                tkimg = Image.fromarray(tkimg)
                imgtk = ImageTk.PhotoImage(image=tkimg)
                video.imgtk=imgtk
                video.configure(image=imgtk)
                video.after(5,rec)
            rec()
        except :
            cap.release()
            cap=cv2.VideoCapture(0)
            messagebox.showinfo("Warning","Please dont move the hands out of the frame")
    
    
    cam()

def quiz():
    def finish():
         messagebox.showinfo("MARK",f"Your Score is {score} out of {len(targets)}" )
         cap.release()

    def next():
        global currentIndex
        if currentIndex +1 < len(targets):
            currentIndex+=1
            question.config(text=f"{currentIndex + 1}. Show the sign for "+targets[currentIndex])


    global lastCapture,currentIndex,score
    
    quizFrame = Frame(mainScreen,height=1100,width=1400,bg="#354044")
    quizFrame.grid(column=2,row=1)
    quizFrame.grid_propagate(False)
    video=Label(quizFrame)
    lastCapture = time.time()
    targets=[]
    for i in range(10):
        targets.append(random.choice(labels[:26]))
    score=0
    currentIndex=0
    question=Label(quizFrame,text=f"{currentIndex + 1}. Show the sign for "+targets[currentIndex],fg="#FFFCEF",bg="#354044",font=("Times",29,"bold"))
    question.place(x=90,y=50)
    nextButton=Button(quizFrame,text="Next",fg="#354044",bg="white",font=("Times",21),command=next)
    nextButton.place(x=700,y=700)
    finishButton=Button(quizFrame,text="Finish",fg="#354044",bg="white",font=("Times",21),command=finish)
    finishButton.place(x=800,y=700)
    def cam():

        global cap
        global camera
        cap = cv2.VideoCapture(0) 
        camera= True
        video.place(x=270,y=130)
        
            
        def rec():
            global lastCapture,currentIndex,score
            if not camera:
                return
            success,img=cap.read()
            if not success:
                
                return
            currentTime= time.time()
            if currentTime - lastCapture >=3:

                hands,image=detector.findHands(img)
                if hands:
                    c=predict(img,quizFrame)
                    lastCapture = currentTime
                    if chr(65+c)==targets[currentIndex]:
                        score+=1
                        currentIndex+=1
                        # print(score)
                        if currentIndex==len(targets):
                            finish()
                            return
                        question.config(text=f"{currentIndex + 1}. Show the sign for "+targets[currentIndex])
                    



            
            tkimg = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            tkimg = Image.fromarray(tkimg)
            imgtk = ImageTk.PhotoImage(image=tkimg)
            video.imgtk=imgtk
            video.configure(image=imgtk)
            video.after(5,rec)
        rec()
    cam()




    
        
        


    



mainScreen = Tk()
currentIndex=0


cap=cv2.VideoCapture(0)
signToTextCam=False
classifier = Classifier("model final\keras_model.h5","model final\labels.txt")
labels = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","Doubt ","Everyone ","Family ","Food ","Hello ","Home ","Let ","Love ","Our ","Share "," ","Stand ","Welcome ",""]
detector=HandDetector(maxHands=2)
mainScreen.title("Learning app for Deaf and Mute")
mainScreen.geometry("1600x1100")
titleLabel = Label(mainScreen,text="Interactive Learning App for Deaf and Mute",fg="#FFFCEF",bg="#800020",font=("Times",34,"bold"))
quotesLabel = Label(mainScreen,text="Communication is not about sound,its about understanding ",fg="#FFFCEF",bg="#800020",font=("courier",25,"bold"))


bgImg = Image.open(r"images\bg\KCHH-Sign-Language-GIrl-and-Therapist.jpg")
bgImg = bgImg.resize((800,530),Image.Resampling.LANCZOS)
bgPht = ImageTk.PhotoImage(bgImg)
videoLabel = Label(mainScreen,image = bgPht)

videoLabel.place(x=510,y=150)
titleLabel.place(x=440,y=80)
quotesLabel.place(x=390,y=700)
mainScreen.config(bg="#800020")
navFrame = Frame(mainScreen , bg="#E2C99E",height=1100,width=330)
navFrame.grid_propagate(False)
learnButton = Button(navFrame,text="Learn",fg = "#F0E7D5",bg="#48192E", font=("courier",23,"bold"),command=learn)
conButton = Button(navFrame,text="Sign to Speech",bg="#48192E",fg = "#F0E7D5", font=("courier",23,"bold"),command=signToText)
testButton = Button(navFrame,text="Quiz",fg = "#F0E7D5",bg="#48192E", font=("courier",23,"bold"),command=quiz)
navFrame.grid(row=1,column=1)
learnButton.place(x=30,y=250)
conButton.place(x=30,y=380)
testButton.place(x=30,y=510)
mainScreen.mainloop()