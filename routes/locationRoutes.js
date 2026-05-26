const express = require("express");
const axios = require("axios");

const router = express.Router();

router.get("/reverse", async (req, res) => {

  try {

    const { lat, lon } = req.query;

    const response = await axios.get(
      "https://us1.locationiq.com/v1/reverse",
      {
        params: {
          key: process.env.LOCATIONIQ_API_KEY,
          lat,
          lon,
          format: "json",
          normalizeaddress: 1
        }
      }
    );

    const data = response.data;

    const address = data.address || {};

    const fullLocation = `
${address.name || ""}
${address.house_number || ""}
${address.road || ""}
${address.neighbourhood || ""}
${address.suburb || ""}
${address.city || ""}
${address.county || ""}
${address.state || ""}
${address.postcode || ""}
${address.country || ""}
    `
      .replace(/\s+/g, " ")
      .trim();

    res.json({
      success: true,
      location: fullLocation,
      fullData: data
    });

  } catch (err) {

    console.log(err.response?.data || err.message);

    res.status(500).json({
      success: false,
      error: "Location fetch failed"
    });

  }

});

module.exports = router;