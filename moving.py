import cv2
import numpy as np
import pandas as pd

def dist(dot1, dot2):
    x1, y1 = dot1
    x2, y2 = dot2
    return np.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

def mouse_event(event, x, y, flags, params):
    if event == cv2.EVENT_MOUSEMOVE:
        print(x,y)

def get_coords(event, x, y, flags, params):
    global central_dot_y, central_dot_x
    if event == cv2.EVENT_LBUTTONUP:
        central_dot_x = x
        central_dot_y = y
        cv2.destroyAllWindows()

frames_array = []

filename = input("Введите название видео (полностью, с расширением):\n")
cap = cv2.VideoCapture("./videos/"+filename); 

ret, frame1 = cap.read()
ret, frame2 = cap.read()

centers = []

#output = ''
print("Видео обрабатывается, ожидайте...")
while cap.isOpened(): 

    frames_array.append(frame1)
    
    # Обработка изображения
 
    diff = cv2.absdiff(frame1, frame2) 
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) 
    blur = cv2.GaussianBlur(gray, (9, 9), 10) 
    _, thresh = cv2.threshold(blur, 5, 255, cv2.THRESH_BINARY) 
    dilated = cv2.dilate(thresh, None, iterations = 3) 
 
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    
    x_arr = []
    y_arr = []
    w_arr = []
    h_arr = []
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour) # Нахождение прямоугольника, описывающего контур
        x_arr.append(x)
        y_arr.append(y)
        w_arr.append(w)
        h_arr.append(h)

        if cv2.contourArea(contour) < 700: 
            continue
    try: # Объединение разных прямоугольников в один (после обработки контур мыши разбивался на несколько областей)
        x = min(x_arr)
        y = min(y_arr)
        w = max(x_arr)-min(x_arr)+min(w_arr)
        h = max(y_arr)-min(y_arr)+min(h_arr)

        center = (x + w/2, y + h/2)
        centers.append(center)
    except ValueError:
        centers.append(centers[len(centers)-1])

    frame1 = frame2
    ret, frame2 = cap.read() 

    if not ret:
        break

cap.release()

# Обработка полученных значений
# dot_data = ((x,y), cor/inc, (c/p, j), stop/move)
dot_data = []
#mouse_length = 135
correct_epsilon = 15
central_radius = 135
central_segment = 55
stop_radius = 20

crossed_central = 0
crossed_periphery = 0

#central_dot_x = int(input("Введите координату x центральной точки: "))
#central_dot_y = int(input("Введите координату y центральной точки: "))
#central_dot = (central_dot_x, central_dot_y)
central_dot_x = 320
central_dot_y = 240

cv2.imshow("Click on central hole", frames_array[1])
cv2.setMouseCallback("Click on central hole", get_coords)
cv2.waitKey(0)

central_dot = (central_dot_x, central_dot_y)
print(central_dot_x, central_dot_y)

x = []
y = []
is_correct = []
is_central = []
sector = []
count_changed_central = []
count_changed_periphery = []
is_moving = []

print("Данные обрабатываются...")

for i in range(1,len(centers)-1):
    x_cen, y_cen = centers[i]
    x.append(x_cen)
    y.append(y_cen)

    # Проверка точки на достоверность
    try:
        if dist(centers[i],centers[i-1]) > correct_epsilon:
            if is_correct[len(is_correct)-1] == False:
                is_correct.append(True)
            else:
                is_correct.append(False)
        else:
            if is_correct[len(is_correct)-1] == False:
                is_correct.append(False)
            else:
                is_correct.append(True)
    except IndexError:
        is_correct.append(False)


    # Проверка точки на центр/перифирию
    mouse_radius = dist(centers[i], central_dot)
    mouse_cos = (x_cen-central_dot_x)/mouse_radius
    mouse_sin = (y_cen-central_dot_y)/mouse_radius

    #s = 0

    if mouse_sin > 0:
        mouse_angle = np.arccos(mouse_cos)
    else:
        mouse_angle = np.pi + np.arccos(mouse_cos)
    if mouse_radius > central_radius:
        is_central.append(False)
        for j in range(1,13):
            if mouse_angle > (j-1)*np.pi/6 and mouse_angle <= j*np.pi/6:
                sector.append(j)
                #s = -j
    if mouse_radius <= central_radius:
        is_central.append(True)
        if mouse_radius <= central_segment:
            sector.append(7)
        else:
            for j in range(1,7):
                if mouse_angle > (j-1)*np.pi/3 and mouse_angle <= j*np.pi/3:
                    sector.append(j)
    if i == 1 or i == 2:
        count_changed_central.append(0)
        count_changed_periphery.append(0)
    elif is_correct[len(is_correct)-1] == True:
        if is_central[len(is_central)-1] == True and is_central[len(is_central)-2] == True:
            if sector[len(sector)-1] != sector[len(sector)-2]:
                count_changed_central.append(count_changed_central[len(count_changed_central)-1] + 1)
                count_changed_periphery.append(count_changed_periphery[len(count_changed_periphery)-1])
            else:
                count_changed_central.append(count_changed_central[len(count_changed_central)-1])
                count_changed_periphery.append(count_changed_periphery[len(count_changed_periphery)-1])
        elif is_central[len(is_central)-1] == False and is_central[len(is_central)-2] == False:
            if sector[len(sector)-1] != sector[len(sector)-2]:
                count_changed_central.append(count_changed_central[len(count_changed_central)-1])
                count_changed_periphery.append(count_changed_periphery[len(count_changed_periphery)-1] + 1)
            else:
                count_changed_central.append(count_changed_central[len(count_changed_central)-1])
                count_changed_periphery.append(count_changed_periphery[len(count_changed_periphery)-1])
        elif is_central[len(is_central)-1] == True and is_central[len(is_central)-2] == False:
            count_changed_central.append(count_changed_central[len(count_changed_central)-1] + 1)
            count_changed_periphery.append(count_changed_periphery[len(count_changed_periphery)-1])
        else:
            count_changed_central.append(count_changed_central[len(count_changed_central)-1])
            count_changed_periphery.append(count_changed_periphery[len(count_changed_periphery)-1] + 1)
    else:
        count_changed_central.append(count_changed_central[len(count_changed_central)-1])
        count_changed_periphery.append(count_changed_periphery[len(count_changed_periphery)-1])
                    
    # Проверка точки на остановку
    if dist(centers[i],centers[i-1]) < stop_radius and dist(centers[i],centers[i+1]) < stop_radius:
        is_moving.append(False)
    else: is_moving.append(True)

#print(len(x), len(y), len(is_correct), len(is_central), len(sector), len(is_moving),sep="\n")

# Запись в файл excel
df = pd.DataFrame({'x': x,
                   'y': y,
                   'Распознано корректно': is_correct,
                   'Находится в центре': is_central,
                   'Сектор': sector,
                   'Количество пересеченных ячеек в центре': count_changed_central,
                   'Количество пересеченных ячееек на периферии': count_changed_periphery,
                   'Двигается ли': is_moving})

df.to_excel('./data/'+filename+'_data.xlsx')

print("Данные успешно записаны в файл:", filename+'_data.xlsx')

i = 1
while True:
    image = cv2.circle(frames_array[i], (int(x[i]),int(y[i])), 5, (0,0,255), -1)
    cv2.namedWindow('Frame = '+str(i))
    cv2.moveWindow('Frame = '+str(i), 50, 50)
    cv2.imshow('Frame = '+str(i), image)
    cv2.setMouseCallback('Frame = '+str(i), mouse_event)
    key = cv2.waitKey(0)
    if key == ord('n') and i < len(frames_array)-1:
        i+=1
    if key == ord('p') and i > 1:
        i-=1
    if key == ord('q'):
        break
    cv2.destroyAllWindows()

cv2.destroyAllWindows()
# file = open("trajectory.txt",'x')
# file.write(output)
# file.close()