# Page snapshot

```yaml
- navigation:
  - link " Quiz Master V2":
    - /url: /
  - list
  - list:
    - listitem:
      - link " Login":
        - /url: /login
    - listitem:
      - link " Register":
        - /url: /register
- main:
  - text: 
  - heading "Login" [level=2]
  - paragraph: Welcome back! Please login to your account.
  - text: Username
  - textbox "Username"
  - text: Password
  - textbox "Password"
  - button "Login"
  - paragraph:
    - text: Don't have an account?
    - link "Register here":
      - /url: /register
```