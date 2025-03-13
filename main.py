import cv2 as cv
import numpy as np

barva_koze = None
klik_tocka = None

def klik_na_kamero(dogodek, x, y, flags, param):
    global klik_tocka, izracunano
    if dogodek == cv.EVENT_LBUTTONDOWN:
        klik_tocka = (x, y)
        izracunano = False

def doloci_barvo_koze(slika, levo_zgoraj, desno_spodaj):
    kvadrat = slika[levo_zgoraj[1]:desno_spodaj[1], levo_zgoraj[0]:desno_spodaj[0]]
    kvadrat_barva = cv.cvtColor(kvadrat, cv.COLOR_BGR2RGB)
    povp_barva = cv.mean(kvadrat_barva)[:3]
    toleranca = 10

    spodnja_meja = np.array([max(0, povp_barva[0] - toleranca), max(0, povp_barva[1] - toleranca), max(0, povp_barva[2] - toleranca)], dtype=np.uint8)
    zgornja_meja = np.array([min(179, povp_barva[0] + toleranca), min(255, povp_barva[1] + toleranca), min(255, povp_barva[2] + toleranca)], dtype=np.uint8)

    return spodnja_meja, zgornja_meja

def zmanjsaj_sliko(slika, sirina, visina):
    return cv.resize(slika, (sirina, visina))

def obdelaj_sliko_s_skatlami(slika, sirina_skatle, visina_skatle, barva_koze):
    pass

def prestej_piksle_z_barvo_koze(slika, barva_koze):
    pass

if __name__ == '__main__':
    kamera = cv.VideoCapture(1)
    if not kamera.isOpened():
        print('Kamera ni bila odprta.')
    else:
        while True:
            ret, slika = kamera.read()
            if not ret:
                print("Napaka pri zajemanju slike.")
                break
            slika = cv.flip(slika, 1)
            slika = zmanjsaj_sliko(slika, 300, 260)
            cv.setMouseCallback('Kamera', klik_na_kamero, slika)

            if klik_tocka is not None and not izracunano:
                visina,sirina = klik_tocka
                visina_pravokotnika = 100
                sirina_pravokotnika = 60
                zgoraj_levo = (visina - sirina_pravokotnika // 2, sirina - visina_pravokotnika // 2)
                spodaj_desno = (visina + sirina_pravokotnika // 2, sirina + visina_pravokotnika // 2)
                cv.rectangle(slika, zgoraj_levo, spodaj_desno, (0, 255, 0))
                spodnja_meja, zgornja_meja = doloci_barvo_koze(slika, zgoraj_levo, spodaj_desno)
                print("Spodnja meja: ", spodnja_meja)
                print("Zgornja meja: ", zgornja_meja)
                izracunano = True

            cv.imshow('Kamera', slika)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        kamera.release()
        cv.destroyAllWindows()