## Funzionalità

### 1. Generazione di nuove specie chimiche

 Dati due file di input (`specie.txt` e `parametri.txt`), genera nuove specie e reazioni chimiche.
```bash
 python ./main.py generate
```
### 2. Tabulazione dei dati in un foglio Excel

 I dati in output dallo step precedente vengono salvati in un file Excel.
```bash 
python ./main.py tabulate
```
### 3. Operazioni combinate

 È possibile eseguire sia la generazione che la tabulazione dei dati in un'unica esecuzione del programma.
```bash
 python ./main.py generate tabulate
```

### 4. Debug
 È possibile visualizzare l'output di generazione e tabulazione via terminale a runtime
```bash
 python ./main.py generate tabulate debug
```
