const express = require("express");
const router = express.Router();

router.get("/reverse", async (req, res) => {
  try {
    const { lat, lon } = req.query;

    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`,
      {
        headers: {
          "User-Agent": "my-app"
        }
      }
    );

    const data = await response.json();
    res.json(data);

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;