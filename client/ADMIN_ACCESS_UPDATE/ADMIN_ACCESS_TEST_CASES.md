# Admin access update: test cases

How to check the new admin and role rules in the TOURISE 2027 admin. 5 October 2026.

## How to use this

- **Who:** anyone on the team. No technical knowledge needed.
- **Where:** the test (development) admin, not production.
- **Time:** about 20 minutes.
- **How:** follow each step and compare with the expected result. Write **Pass** or **Fail** in the last column. For a Fail, send the case number and a screenshot.

> Use a normal browser window for the Super Admin and a **private (incognito) window** for the other test admins, so you can stay logged in as both.

## Before you start (as Super Admin)

1. In **Roles**, create three roles:
   - **Client Manager:** Admins Management (View, Create, Update, Block), Categories (View, Update), Titles (View)
   - **Desk:** Titles (View)
   - **Stronger:** Titles (View, Update)
2. In **Admins**, create three admins:
   - **Client**, role *Client Manager*, Data scope: one category, for example *Media*
   - **Desk User**, role *Desk*, category *Media*
   - **Strong User**, role *Stronger*, category *Media*
3. Log in as **Client** in a private window.

## A. As the client manager (Client)

| # | Steps | Expected result | Pass / Fail |
|---|---|---|---|
| 1 | Look at the sidebar | There is **no Roles** link | |
| 2 | Open **Admins** | Desk User and Strong User are listed. **No Super Admin** appears | |
| 3 | Click **New admin** and open the role picker | **Desk** and **Client Manager** are offered (and any other role with only permissions Client has). **No Super Admin, no Stronger** | |
| 4 | Create an admin with role *Desk* and category *Media* | **Saved** | |
| 5 | Create an admin with a category other than *Media* | Refused: "This gives access to guests you cannot see yourself." | |
| 6 | Open **your own** record (Client) to edit | Role, Status and Data scope are **greyed out**, with a note that another admin can change them | |
| 7 | On your own record, change your first name and save | **Saved** | |
| 8 | In the Admins list, look at your own row | There is **no Block** action | |
| 9 | Edit **Strong User**, set a new password, save | Refused: "This admin has permissions you do not have." | |
| 10 | **Block** Strong User | Refused with the same message | |
| 11 | Log in as **Desk User** in another browser, then as Client **block** Desk User | Desk User is **logged out** on their next click | |
| 12 | Open a **category**, go to **Admin access** | Desk User (and the admin from step 4) are offered. **Not** you, not Strong User, not a Super Admin | |
| 13 | Save that category | Strong User and you **keep** your access to it | |
| 14 | Type the Roles page address in the browser (`/en/roles`) | The page does **not** open | |

## B. Roles (as Super Admin, tick Roles View, Create and Update on *Client Manager*; then back as Client)

| # | Steps | Expected result | Pass / Fail |
|---|---|---|---|
| 15 | Look at the sidebar | The **Roles** link now shows | |
| 16 | Click **Create role** | Only **your own** permissions are offered: Admins Management, Roles, Categories and Titles (View) | |
| 17 | Look at the *Client Manager* row in the Roles list | There is **no Edit** and **no Delete** (it is your own role) | |
| 18 | Open the *Stronger* role and save it | Refused: "This role has permissions you do not have." | |
| 19 | Look for the **Super Admin** role | It is **not** in the list | |

## C. As Super Admin (nothing should change)

| # | Steps | Expected result | Pass / Fail |
|---|---|---|---|
| 20 | Open **Admins** and **Roles** | Everything is visible, Super Admin included | |
| 21 | Edit any admin or role, block and unblock an admin | Everything **works** as before | |

## Reporting

Send the case number, what you saw, and a screenshot to the admin team. If everything passes, reply "All 21 pass".
