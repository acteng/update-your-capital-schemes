# User guide

## Generating the user guide

To generate the user guide:

```bash
cd docs/user-guide
./generate.sh
```

Open `index.pdf`.

## Creating the screenshots

To recreate the screenshots used in the user guide:

1. [Run the service locally](../../README.md#running-locally)
1. [Load the example dataset](../../data/README.md#loading-the-example-dataset)
1. Open a browser window with viewport dimensions of 1280x1024
1. Follow the actions detailed below, capturing a screenshot after each step and saving it with the specified filename:

   | Action                                                                                                         | Screenshot                 |
   |----------------------------------------------------------------------------------------------------------------|----------------------------|
   | Open [Prod](https://update-your-capital-schemes.activetravelengland.gov.uk/)                                   | start.png                  |
   | Click "Start now"                                                                                              | create-or-sign-in.png      |
   | Click "Create your GOV.UK One Login"                                                                           | create-enter-email.png     |
   | Enter "update-your-capital-schemes@activetravelengland.gov.uk" and click "Continue"                            | create-check-email.png     |
   | Check the email, enter the code, click "Continue"                                                              | create-password.png        |
   | Generate a password, enter it twice, click "Continue"                                                          | create-security-codes.png  |
   | Check "Authenticator app" and click "Continue"                                                                 | create-qr-code.png         |
   | Click "I cannot scan the QR code"                                                                              | create-secret-key.png      |
   | Use the secret key to generate a code, enter the code, click "Continue"                                        | create-success.png         |
   | Open [Local](http://127.0.0.1:5000/) and sign in                                                               | schemes.png                |
   | Open [Prod](https://update-your-capital-schemes.activetravelengland.gov.uk/), click "Start now" then "Sign in" | sign-in-enter-email.png    |
   | Enter email and click "Continue"                                                                               | sign-in-password.png       |
   | Enter password and click "Continue"                                                                            | sign-in-security-code.png  |
   | Open [Local](http://127.0.0.1:5000/), sign in and click "ATE00123"                                             | scheme.png                 |
   | Next to "Spent to date" click "Change"                                                                         | change-spend-to-date.png   |
   | Click "Cancel", next to "Milestones" click "Change"                                                            | change-milestone-dates.png |
   | Click "Cancel", scroll to the bottom, check "I confirm that..."                                                | review.png                 |
   | Click "Confirm"                                                                                                | review-success.png         |

1. [Delete the GOV.UK One Login account](https://home.account.gov.uk/security) for update-your-capital-schemes@activetravelengland.gov.uk
