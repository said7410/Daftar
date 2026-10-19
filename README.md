# @manhwatarjima2_bot - Oracle Cloud (Ampere A1) nusxasi

Sinov nusxasi: @manhwatarjima_bot bilan AYNAN bir xil kod (githupuchun222-creator/manhwa-bot),
lekin Cloudflare darvozasi va runner.py ISHLATILMAYDI - VPS 24/7 yoniq, shuning uchun bot
to'g'ridan-to'g'ri Telegram'dan xabar oladi (polling), systemd uni qayta yoqib turadi.

## Fayllar
- `oracle-setup.sh` - serverda bir marta ishga tushiriladi (paketlar, kod, venv, LaMa, systemd)
- `.env` - sozlamalar va kalitlar (SIR: hech qayerga yuklanmaydi, 600 huquq)

## O'rnatish (server tayyor bo'lgandan keyin)
```
scp -i <kalit> oracle-setup.sh .env ubuntu@<IP>:~/
ssh -i <kalit> ubuntu@<IP> 'bash oracle-setup.sh'
```

## Kundalik buyruqlar
```
journalctl -u manhwa-bot -f                 # jonli log
sudo systemctl restart manhwa-bot           # qayta ishga tushirish
cd ~/manhwa-bot && git pull && sudo systemctl restart manhwa-bot   # kodni yangilash
```

## Eslatmalar
- Gemini kaliti hozircha @manhwatarjima_bot bilan BIR XIL - kunlik limit birga sarflanadi.
  Sinovdan keyin bu botga alohida kalit kerak.
- Ma'lumot (obuna, tarix, balans) serverdagi `admins.json` da, 4-bot bilan aralashmaydi.
- Katta fayllar (>20 MB) uchun TG_API_ID/TG_API_HASH 4-bot bilan bir xil - bu normal.
