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

    console.log(req.file);

    const imageResponse = await axios({
  url: req.file.path,
  method: "GET",
  responseType: "stream"
});

const FormData = require("form-data");

const formData = new FormData();

// send Cloudinary image URL directly
formData.append("image", req.file.path);

const detectRes = await axios.post(
  `${process.env.PYTHON_API_URL}/detect`,
  formData,
  {
    headers: formData.getHeaders()
  }
);

console.log(detectRes.data);

const hasIdCard = detectRes.data.id_card_detected;

const newPerson = new Person({
  name: req.body.name,
  dob: req.body.dob,
  department: req.body.department,
  phone: req.body.phone,
  email: req.body.email,
  location: req.body.location,
  photo: req.file.path,
  idCard: hasIdCard
});

    await newPerson.save();

    res.json({
      success: true,
      data: newPerson
    });

  } catch (error) {

  console.log("FULL ERROR:");

  console.log(error);

  if (error.response) {
    console.log("PYTHON ERROR DATA:");
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