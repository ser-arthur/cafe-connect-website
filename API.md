# API Documentation for CafeConnect

## Overview

This document provides an overview of interacting with the CafeConnect API. It includes details on endpoints, request formats,
response formats, and validation rules.

## Base URL

```
http://localhost:5000/api     # localhost address may vary depending on your system
```

## Authentication
To interact with the API, users need to create an account on the website. After registering, users can log in to obtain a token, which is required for accessing protected routes.

**Admin Credentials for Testing**:

For testing purposes, you can use the following admin credentials to access routes requiring admin privileges:
```bash
  Email: darthvader@gmail.com
  Password: anakinsky@2024
```


### Login
- **Endpoint:** `/login`  
- **Method:** `POST`  
- **Description:** Authenticates a user and returns a token. This token must be included in the header of any protected routes.

**Headers:** None

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**

```json
{
  "token": "your-jwt-token"
}
```

**Token Authentication**

To access protected routes, include the token in the header:

```bash
Authorization: Bearer your-jwt-token
```

**Protected Routes**

The following routes require user authentication (i.e., a valid token):

* Get all cafes: **GET** `/cafes`
* Get a cafe by ID: **GET** `/cafes/<int:cafe_id>`
* Add Cafe: **POST** `/cafes`

The following routes require admin privileges (i.e., a valid token with admin access):

* Update Cafe: PUT `/cafes/<int:cafe_id>`
* Delete Cafe: DELETE `/cafes/<int:cafe_id>`

## Endpoints

### 1. Fetch All Cafes

- **Endpoint:** `/cafes`
- **Method:** `GET`
- **Description:** Returns a list of all cafes.

**Response:**

```json
[
  {
    "id": 1,
    "name": "Cafe Name",
    "map_url": "http://map.url",
    "city": "City",
    "country": "Country",
    "currency": "Currency",
    "coffee_price": "5.00",
    "wifi_strength": 4,
    "seats": 50,
    "has_sockets": true,
    "has_toilet": false,
    "images": "image1.jpg,image2.jpg",
    "full_review": "Great cafe!",
    "full_rating": 5
  }
]
```

### 2. Fetch a Cafe by ID

- **Endpoint:** `/cafes/<int:cafe_id>`
- **Method:** `GET`
- **Description:** Retrieves details of a specific cafe by its ID.

**Response:**

```json
{
  "id": 1,
  "name": "Cafe Name",
  "map_url": "http://map.url",
  "city": "City",
  "country": "Country",
  "currency": "Currency",
  "coffee_price": "5.00",
  "wifi_strength": 4,
  "seats": 50,
  "has_sockets": true,
  "has_toilet": false,
  "images": "image1.jpg,image2.jpg",
  "full_review": "Great cafe!",
  "full_rating": 5
}
```

### 3. Add New Cafe

- **Endpoint:** `/cafes`
- **Method:** `POST`
- **Description:** Adds a new cafe to the database.

**Request Body:**

```json
{
  "name": "New Cafe",
  "map_url": "http://map.url",
  "city": "City",
  "country": "Country",
  "coffee_price": "5.00",
  "currency": "Currency",
  "wifi_strength": 4,
  "seats": 20,
  "has_sockets": true,
  "has_toilet": false,
  "images": "image1-link.jpg,image2-link.jpg",
  "full_review": "Great cafe!",
  "full_rating": 4
}
```

**Response:**

```json
{
  "message": "Cafe added successfully."
}
```

### 4. Update Cafe

- **Endpoint:** `/cafes/int:cafe_id`
- **Method:** `PUT`
- **Description:** Allows an authenticated `admin` to update the details of an existing a cafe by its ID.

**Request Body:**

```json
{
  "name": "Updated Cafe Name",
  "map_url": "http://updated.map.url",
  "city": "Updated City",
  "country": "Updated Country",
  "coffee_price": "6.00",
  "currency": "Updated Currency",
  "wifi_strength": 5,
  "seats": 30,
  "has_sockets": true,
  "has_toilet": false,
  "images": "link-to-updated-image.jpg, link-to-updated_image2.jpg",
  "full_review": "Updated review!",
  "full_rating": 5
}
```

**Response:**

```json
{
  "message": "<Updated Cafe Name> updated successfully!",
  "cafe": {
    "id": 1,
    "name": "Updated Cafe Name",
    "map_url": "http://updated.map.url",
    "city": "Updated City",
    "country": "Updated Country",
    "currency": "Updated Currency",
    "coffee_price": "6.00",
    "wifi_strength": 5,
    "seats": 30,
    "has_sockets": true,
    "has_toilet": false,
    "images": "link-to-updated-image.jpg, link-to-updated_image2.jpg",
    "full_review": "Updated review!",
    "full_rating": 5
  }
}
```

### Delete Cafe

- **Endpoint:**  `/cafes/int:cafe_id `
- **Method:**  `DELETE `
- **Description:** Allows an authenticated `admin` to delete a cafe by its ID.

**Response:**

```json
{
  "message": "<Cafe Name> deleted successfully!"
}
```

## Error Handling

All API errors are returned in the following format:
```bash
  {
    "message": "Description of the error"
  }
```

### Status Codes

* **200 OK**: The request was successful.
* **201 Created**: A new resource was successfully created.
* **400 Bad Request**: The request data was invalid or incomplete.
* **401 Unauthorized**: Authentication failed or the user does not have permission.
* **404 Not Found**: The requested resource was not found.
* **429 Too Many Requests**: The client has sent too many requests in a given amount of time.
* **500 Internal Server Error**: Something went wrong on the server.

## Data Format & Validation

### Country

- **Format:** `String`
- **Values:**
    - Australia (AU)
    - Canada (CA)
    - Germany (DE)
    - … (See full list in the `COUNTRIES` variable in ```app/main/data.py```)

### Currency

- **Format:** `String`
- **Values:**
    - `$`
    - `€`
    - `₹`
    - … (See full list in the `CURRENCIES` variable in ```app/main/data.py```)

### Coffee Price

- **Format:** `String`
- **Example:** `"5.00"`

### Wifi Strength

- **Format:** `Integer`
- **Values:** `0` to `5`

### Full Rating

- **Format:** `Integer`
- **Values:** `1` to `5`
