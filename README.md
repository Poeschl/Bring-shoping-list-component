# Bring! Shopping List Component

This component integrates the [Bring! Shopping List app](https://getbring.com/) into Home Assistant.
To display your shopping lists on the lovelace UI use the [Bring! Shopping List Card](https://github.com/dotKrad/bring_shopping_list_card). 

# Installation

## HACS

Install it in the `Integrations` tab on the [Home Asssistant Community Store](https://github.com/custom-components/hacs).

## Manual way
To use it, copy the `bring_shopping_list` folder inside your `config/custom_components` folder on your Home Assistant installation first.

## Configuration

```
bring_shopping_list:
  username: user
  password: password
  lists:
    - id: xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
      name: Home
      locale: en-US
    - id: xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
      name: Work
      locale: de-DE
```

#### `username`
Your username of Bring!

#### `password`
Your password of Bring!

#### `lists`
This contains the lists you want to monitor.
Take a look below for the element syntax.

### List entry

#### `id`
The list id. (TODO: Step-by-step how to get it)

#### `name` (Optional)
This is used to make sensor name friendly otherwise id will be used. Example sensor.bring_shopping_list_home

#### `locale` (Optional)
Locale used to get the name of the items. (Default: `en-US`)
