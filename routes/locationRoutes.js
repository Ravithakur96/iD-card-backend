const express = require("express");
const router = express.Router();

router.get("/reverse", async (req, res) => {

  try {

    const { lat, lon } = req.query;

    if (!lat || !lon) {
      return res.status(400).json({
        success: false,
        message: "Latitude and Longitude required"
      });
    }

    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&addressdetails=1&zoom=18`,
      {
        headers: {
          "User-Agent": "mern-location-app"
        }
      }
    );

    const data = await response.json();

    const address = data.address || {};

    // Better readable location
    const fullLocation = {
      houseNumber: address.house_number || "",
      road: address.road || "",
      village: address.village || "",
      suburb: address.suburb || "",
      city:
        address.city ||
        address.town ||
        address.county ||
        "",
      state: address.state || "",
      country: address.country || "",
      postcode: address.postcode || "",
      fullAddress: data.display_name || ""
    };

    res.json({
      success: true,
      location: fullLocation
    });

  } catch (err) {

    res.status(500).json({
      success: false,
      error: err.message
    });

  }

});

module.exports = router;