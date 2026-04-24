# Machine Vision

### Pictures Unzip Automation (in terminal):
```bash
find pics -name "*.zip" -exec sh -c 'unzip -o "$1" -d "$(dirname "$1")"' _ {} \;
```

## IMAGE PROCESSING

### Čo tento program robí

Program dostane obrázok fólie a určuje či je fólia poškodená alebo je v poriadku

Program vracia:

* **PASS** → fólia je OK
* **FAIL** → fólia je poškodená

---

## Ako main.py funguje

Predstav si to ako postup, ktorý by robil človek:

### 1. Zjednodušenie obrázka

* obrázok sa prevedie na **čiernobiely**
* jemne sa rozmaže → odstráni sa šum

---

### 2. Hľadanie hrán

Program hľadá všetky „ostré prechody“ v obraze
→ teda miesta, kde sa mení farba

Výsledok:

* čierny obrázok
* biele čiary = možné škrabance

---

### 3. Odstránenie okrajov

Okraje obrázka často obsahujú:

* stôl
* svetlo
* okraj fólie

Program ich **odreže**

---

### 4. Nájde sa oblasť fólie (ROI)

Program sa snaží určiť:

> kde je samotná fólia a kde už nie

Vytvorí masku:

* biela = fólia
* čierna = ignorovať

---

### 5. Nechá iba škrabance na fólii

* hrany sa „prekryjú“ s maskou fólie

ostanú len čiary, ktoré sú:
* na fólii
* a vyzerajú ako škrabance

---

### 6. Ztenčenie čiar (skeleton)

Každá čiara sa zmení na:

* **tenkú 1-pixelovú čiaru**

---

### 7. Výpočet poškodenia

Program spočíta:

> koľko pixelov tvoria škrabance

```text
scratch_length = počet pixelov čiar
```

---

### 8. Rozhodnutie

Program má hranicu (threshold):

```text
ak je dĺžka veľká → FAIL
ak je malá → PASS
```

---

## Výsledok

V termináli:

```text
image.png -> scratch_length=4853, result=FAIL
```

* našlo sa veľa škrabancov
* fólia je poškodená

---

## Použité nastavenia

```bash
THRESHOLD_LENGTH = 1500

CANNY:
    low = 30
    high = 100

BLUR:
    kernel = (5,5)

ROI:
    threshold = 170

BORDER REMOVAL:
    margin ≈ 7%
```

## Čo robilo problémy

### 1. Hrana fólie

* horný okraj vyzerá ako škrabanec
  → spôsoboval chyby

---

### 2. Pozadie mimo fólie

* niekedy malo podobnú farbu

---

### 3. Natočené obrázky

* keď je fólia veľmi otočená → detekcia horšia