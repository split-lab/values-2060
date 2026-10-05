# Deployment details

- Google Sheet: https://docs.google.com/spreadsheets/d/1EArH4vhul4-a65NPYLi71LgnO3I1-351as7QVxyM5x4/edit
- Apps Script ID: 1rkvyb4O0hBE_EUW7oZ3dwPpN8u6rCadMp8wLT_b-HSTUosis2jdhMsFp
- Script editor: https://script.google.com/d/1rkvyb4O0hBE_EUW7oZ3dwPpN8u6rCadMp8wLT_b-HSTUosis2jdhMsFp/edit
- Web app deployment ID (v1): AKfycbzHFlhaO3dbdsQQRCqDiKJd4E5fmkkgXP--LVkTUXRyfpTkMSFpGsT0mYu-umcJji3K
- Web app URL: https://script.google.com/macros/s/AKfycbzHFlhaO3dbdsQQRCqDiKJd4E5fmkkgXP--LVkTUXRyfpTkMSFpGsT0mYu-umcJji3K/exec

## After editing backend/Code.gs
Always redeploy to the SAME deployment ID, so the survey URL keeps working:

    cd backend
    clasp push --force
    clasp create-deployment -i AKfycbzHFlhaO3dbdsQQRCqDiKJd4E5fmkkgXP--LVkTUXRyfpTkMSFpGsT0mYu-umcJji3K -d "v2"
