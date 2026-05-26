const express = require("express");
const multer = require("multer");
const cloudinary = require("cloudinary").v2;
const { CloudinaryStorage } = require("multer-storage-cloudinary");
const Person = require("../models/person");
const axios = require("axios");
const FormData = require("form-data");


const router = express.Router();

cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
});

const storage = new CloudinaryStorage({
  cloudinary,
  params: {
    folder: "mern_profiles",
    allowed_formats: ["jpg", "png", "jpeg"],
  },
});

const upload = multer({ storage });

router.post("/", upload.single("photo"), async (req, res) => {
  try {

    if (!req.file) {
      return res.status(400).json({
        error: "No file uploaded"
      });
    }

    console.log(req.file.path);

    console.log(process.env.PYTHON_API_URL);

    const detectRes = await axios.post(
      `${process.env.PYTHON_API_URL}/detect`,
      {
        image_url: req.file.path
      }
    );

    console.log(detectRes.data);

    if (!detectRes?.data?.id_card_detected) {

  return res.status(400).json({
    success: false,
    message: "Please upload clear ID Card photo",
    idCard: false
  });

}

    const newPerson = new Person({
      name: req.body.name,
      dob: req.body.dob,
      department: req.body.department,
      phone: req.body.phone,
      email: req.body.email,
      location: req.body.location,
      photo: req.file.path,
      idCard: detectRes.data.id_card_detected
    });

    await newPerson.save();

    res.json({
      success: true,
      data: newPerson
    });

  } catch (error) {

    console.log("FULL ERROR => ", error.message);

if (error.response) {
  console.log("DATA =>", error.response.data);
  console.log("STATUS =>", error.response.status);
}

if (error.request) {
  console.log("NO RESPONSE FROM PYTHON API");
}

    if (error.response) {
      console.log(error.response.data);
    }

    res.status(500).json({
      error: error.message
    });
  }
});

router.get("/", async (req, res) => {
  const data = await Person.find();
  res.json(data);
});

module.exports = router;