import cv2 as cv
import numpy as np
import time

klik_tocka = None
izracunano = False
fps = 1

def klik_na_kamero(dogodek, x, y, flags, param):
    global klik_tocka, izracunano
    if dogodek == cv.EVENT_LBUTTONDOWN:
        #Ko se klikne na sliko se shrani x in y koordinate
        klik_tocka = (x, y)
        izracunano = False

def doloci_barvo_koze(slika,levo_zgoraj,desno_spodaj) -> tuple:

    #Kvadrat od klika na kamero
    kvadrat = slika[levo_zgoraj[1]:desno_spodaj[1], levo_zgoraj[0]:desno_spodaj[0]]
    #pretvori se v hsv
    kvadrat_barva = cv.cvtColor(kvadrat, cv.COLOR_BGR2HSV)
    #Dobi se povprecna barva kvadrata
    povp_barva = cv.mean(kvadrat_barva)[:3]
    toleranca = 40

    #Tu se nastavi max ker ce bi bilo stevilo negativno potem nebi blo v pravem formatu in ze zaokrozi
    #isto z min samo da ce slucajno preseze najvecje vrednosti
    spodnja_meja = np.array([max(0, povp_barva[0] - toleranca), max(0, povp_barva[1] - toleranca), max(0, povp_barva[2] - toleranca)], dtype=np.uint8)
    zgornja_meja = np.array([min(179, povp_barva[0] + toleranca), min(255, povp_barva[1] + toleranca), min(255, povp_barva[2] + toleranca)], dtype=np.uint8)

    return spodnja_meja, zgornja_meja

def zmanjsaj_sliko(slika, sirina, visina):
    return cv.resize(slika, (sirina, visina))


def obdelaj_sliko_s_skatlami(slika, sirina_skatle, visina_skatle, barva_koze) -> list:
    #Visina in sirina slike
    visina_slike, sirina_slike = slika.shape[:2]
    skatle = []

    #i se pomika po visini slike (vrstice)
    for i in range(0, visina_slike - visina_skatle + 1, visina_skatle):
        vrstica = []
        #j se pomika po širini slike (stolpci)
        for j in range(0, sirina_slike - sirina_skatle + 1, sirina_skatle):
            piksli_koze = prestej_piklse_z_barvo_koze(slika, barva_koze, (j, i, j + sirina_skatle, i + visina_skatle))
            skupno_pikslov = sirina_skatle * visina_skatle

            #Ce je vec kot 75% pikslov koze potem se appenda kot 1 drugace 0
            if piksli_koze > skupno_pikslov * 0.75:
                vrstica.append(1)
            else:
                vrstica.append(0)

        skatle.append(vrstica)

    return skatle

def prestej_piklse_z_barvo_koze(slika, barva_koze, skatla) -> int:

    #visina1 in sirina 1 sta zgornji levi kot, 2 pa spodnji desni kot
    visina1, sirina1, visina2, sirina2 = skatla
    #Dobi se slika znotraj skatle
    skatla_slika = slika[sirina1:sirina2, visina1:visina2]
    # Pretvori se v hsv
    skatla_slika_hsv = cv.cvtColor(skatla_slika, cv.COLOR_BGR2HSV)

    spodnja_meja, zgornja_meja = barva_koze
    #Range barv ki so med spodnjo in zgornjo mejo v skatli
    koza = cv.inRange(skatla_slika_hsv, spodnja_meja, zgornja_meja)

    #Presteje piksle z barvo koze
    piksli = cv.countNonZero(koza)
    return piksli

if __name__ == '__main__':
    kamera = cv.VideoCapture(1)
    if not kamera.isOpened():
        print('Kamera ni bila odprta.')
    else:
        cv.namedWindow('Kamera')
        cv.setMouseCallback('Kamera', klik_na_kamero)

        barva_koze = None
        prejsnji_cas = time.time()
        visina_skatle = 5
        sirina_skatle = 5

        while True:
            #Izracun fps
            #pomoc z https://www.geeksforgeeks.org/python-displaying-real-time-fps-at-which-webcam-video-file-is-processed-using-opencv/
            trenutni_cas = time.time()
            casovna_razlika = trenutni_cas - prejsnji_cas
            fps = 1 / (trenutni_cas - prejsnji_cas)
            prejsnji_cas = trenutni_cas

            ret, slika = kamera.read()
            if not ret:
                print("Napaka pri zajemanju slike.")
                break
            slika = cv.flip(slika, 1)
            slika = zmanjsaj_sliko(slika, 300, 260)

            if klik_tocka is not None and not izracunano:
                #Ko se klikne na sliko se shrani x in y koordinate
                visina, sirina = klik_tocka
                visina_pravokotnika = 100
                sirina_pravokotnika = 60
                #Zgoraj levi in spodaj desni kot pravokotnika
                zgoraj_levo = (visina - sirina_pravokotnika // 2, sirina - visina_pravokotnika // 2)
                spodaj_desno = (visina + sirina_pravokotnika // 2, sirina + visina_pravokotnika // 2)
                cv.rectangle(slika, zgoraj_levo, spodaj_desno, (0, 255, 0))
                barva_koze = doloci_barvo_koze(slika, zgoraj_levo, spodaj_desno)

                print("Spodnja meja:", barva_koze[0])
                print("Zgornja meja:", barva_koze[1])
                izracunano = True

            if barva_koze is not None:
                skatle = obdelaj_sliko_s_skatlami(slika, sirina_skatle, visina_skatle, barva_koze)
                visina_slike, sirina_slike = slika.shape[:2]
                for i in range(0, visina_slike - visina_skatle + 1, visina_skatle):
                    # j se pomika po širini slike (stolpci)
                    for j in range(0, sirina_slike - sirina_skatle + 1, sirina_skatle):
                        #// zato da ne gre out of range (pomikanje po pikslih)
                        if skatle[i//visina_skatle][j//sirina_skatle] == 1:
                            cv.rectangle(slika, (j, i), (j + sirina_skatle, i + visina_skatle), (0, 255, 0), 1)
                cv.putText(slika, f"FPS: {int(fps)}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv.imshow('Kamera', slika)
            else:
                #pred klikom
                cv.imshow('Kamera', slika)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        kamera.release()
        cv.destroyAllWindows()