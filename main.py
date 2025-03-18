import cv2 as cv
import numpy as np
import time

klik_tocka = None
izracunano = False
fps = 0

def klik_na_kamero(dogodek, x, y, flags, param):
    global klik_tocka, izracunano
    if dogodek == cv.EVENT_LBUTTONDOWN:
        klik_tocka = (x, y)
        izracunano = False

def doloci_barvo_koze(slika,levo_zgoraj,desno_spodaj) -> tuple:

    kvadrat = slika[levo_zgoraj[1]:desno_spodaj[1], levo_zgoraj[0]:desno_spodaj[0]]
    kvadrat_barva = cv.cvtColor(kvadrat, cv.COLOR_BGR2RGB)
    povp_barva = cv.mean(kvadrat_barva)[:3]
    toleranca = 10

    #Tu se nastavi max ker ce bi bilo stevilo negativno potem nebi blo v pravem formatu in ze zaokrozi
    #isto z min samo da ce slucajno preseze 250 (rgb)
    spodnja_meja = np.array([max(0, povp_barva[0] - toleranca), max(0, povp_barva[1] - toleranca), max(0, povp_barva[2] - toleranca)], dtype=np.uint8)
    zgornja_meja = np.array([min(179, povp_barva[0] + toleranca), min(255, povp_barva[1] + toleranca), min(255, povp_barva[2] + toleranca)], dtype=np.uint8)

    return spodnja_meja, zgornja_meja

def zmanjsaj_sliko(slika, sirina, visina):
    return cv.resize(slika, (sirina, visina))


def obdelaj_sliko_s_skatlami(slika, sirina_skatle, visina_skatle, barva_koze) -> list:
    visina_slike, sirina_slike = slika.shape[:2]
    skatle = []
    slika_Rgb = cv.cvtColor(slika, cv.COLOR_BGR2RGB)
    slika_grid = slika.copy()

    spodnja_meja, zgornja_meja = barva_koze

    #i se pomika po visini slike (vrstice)
    for i in range(0, visina_slike, visina_skatle):
        #j se pomika po širini slike (stolpci)
        for j in range(0, sirina_slike, sirina_skatle):
            cv.rectangle(slika_grid, (j, i), (j + sirina_skatle, i + visina_skatle), (50, 50, 50), 1)
            skatla = slika_Rgb[i:i + visina_skatle, j:j + sirina_skatle]

            barve_med_mejami = cv.inRange(skatla, spodnja_meja, zgornja_meja)

            if np.any(barve_med_mejami):
                skatle.append((j, i, j + sirina_skatle, i + visina_skatle))
                cv.rectangle(slika_grid, (j, i), (j + sirina_skatle, i + visina_skatle), (0, 0, 255), 2)

    return skatle, slika_grid

def prestej_piklse_z_barvo_koze(slika, barva_koze, skatla) -> int:

    visina1, sirina1, visina2, sirina2 = skatla
    skatla_slika = slika[sirina1:sirina2, visina1:visina2]

    skatla_slika_rgb = cv.cvtColor(skatla_slika, cv.COLOR_BGR2RGB)

    spodnja_meja, zgornja_meja = barva_koze
    koza = cv.inRange(skatla_slika_rgb, spodnja_meja, zgornja_meja)

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

        while True:
            ret, slika = kamera.read()
            if not ret:
                print("Napaka pri zajemanju slike.")
                break
            slika = cv.flip(slika, 1)
            slika = zmanjsaj_sliko(slika, 300, 260)

            if klik_tocka is not None and not izracunano:
                visina, sirina = klik_tocka
                visina_pravokotnika = 100
                sirina_pravokotnika = 60
                zgoraj_levo = (visina - sirina_pravokotnika // 2, sirina - visina_pravokotnika // 2)
                spodaj_desno = (visina + sirina_pravokotnika // 2, sirina + visina_pravokotnika // 2)
                cv.rectangle(slika, zgoraj_levo, spodaj_desno, (0, 255, 0))
                barva_koze = doloci_barvo_koze(slika, zgoraj_levo, spodaj_desno)

                print("Spodnja meja:", barva_koze[0])
                print("Zgornja meja:", barva_koze[1])
                izracunano = True

            if barva_koze is not None:
                #Mreza z barvami koze (rdeca)
                skatle, slika_z_mrezo = obdelaj_sliko_s_skatlami(slika, 20, 20, barva_koze)

                for skatla in skatle:
                    piksli_barve_koze = prestej_piklse_z_barvo_koze(slika, barva_koze, skatla)
                    print(f"Število pikslov barve kože v škatli {skatla}: {piksli_barve_koze}")

                cv.imshow('Kamera', slika_z_mrezo)
            else:
                #osnovna mreža
                slika_z_mrezo = slika.copy()
                visina_slike, sirina_slike = slika.shape[:2]
                for i in range(0, visina_slike, 20):
                    for j in range(0, sirina_slike, 20):
                        cv.rectangle(slika_z_mrezo, (j, i), (j + 20, i + 20), (50, 50, 50), 1)
                cv.imshow('Kamera', slika_z_mrezo)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        kamera.release()
        cv.destroyAllWindows()