const express = require("express");
const multer = require("multer");
const cloudinary = require("cloudinary").v2;
const { CloudinaryStorage } = require("multer-storage-cloudinary");
const Person = require("../models/person");
const axios = require("axios");

const router = express.Router();

// ============================
// CLOUDINARY CONFIG
// ============================

cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
});

// ============================
// STORAGE
// ============================

const storage = new CloudinaryStorage({
  cloudinary,
  params: {
    folder: "mern_profiles",
    allowed_formats: ["jpg", "png", "jpeg"],
  },
});

const upload = multer({ storage });

// ============================
// CREATE PERSON
// ============================

router.post(
  "/",
  upload.fields([
    {
      name: "photo",
      maxCount: 1,
    },
    {
      name: "idCardPhoto",
      maxCount: 1,
    },
  ]),
  async (req, res) => {

    try {

      // ============================
      // VALIDATION
      // ============================

      if (
        !req.files ||
        !req.files.photo ||
        !req.files.idCardPhoto
      ) {

        return res.status(400).json({
          success: false,
          message:
            "Both profile photo and ID Card image are required",
        });

      }

      // ============================
      // IMAGE PATHS
      // ============================

      const profileImage =
        req.files.photo[0].path;

      const idCardImage =
        req.files.idCardPhoto[0].path;

      console.log("PROFILE IMAGE:");
      console.log(profileImage);

      console.log("ID CARD IMAGE:");
      console.log(idCardImage);

      // ============================
      // DETECT API
      // ============================

      const detectRes = await axios.post(
        `${process.env.PYTHON_API_URL}/detect`,
        {
          image_url: profileImage,
        },
        {
          timeout: 60000,
        }
      );

      console.log("DETECTION RESPONSE:");
      console.log(detectRes.data);

      // ============================
      // IDCARD NOT DETECTED
      // ============================

      if (
        !detectRes?.data?.id_card_detected
      ) {

        return res.status(400).json({
          success: false,
          message:
            "Please upload a clear profile photo with visible ID Card.",
          idCard: false,
        });

      }

      // ============================
      // OCR API
      // ============================

      const ocrRes = await axios.post(
        `${process.env.PYTHON_API_URL}/ocr`,
        {
          image_url: idCardImage,
        },
        {
          timeout: 60000,
        }
      );

      console.log("OCR RESPONSE:");
      console.log(ocrRes.data);

      // ============================
      // SAVE DATABASE
      // ============================

      const newPerson = new Person({

        name: req.body.name,

        dob: req.body.dob,

        department: req.body.department,

        phone: req.body.phone,

        email: req.body.email,

        location: req.body.location,

        photo: profileImage,

        idCardImage: idCardImage,

        idCard:
          detectRes.data.id_card_detected,

        ocrData:
          ocrRes?.data?.data || {},

      });

      await newPerson.save();

      // ============================
      // SUCCESS RESPONSE
      // ============================

      res.json({
        success: true,
        message:
          "Profile saved successfully",
        data: newPerson,
      });

    } catch (error) {

      console.log("===== FULL ERROR =====");

      console.log(error.message);

      if (error.response) {

        console.log("STATUS:");
        console.log(error.response.status);

        console.log("DATA:");
        console.log(error.response.data);

      }

      if (error.request) {

        console.log(
          "NO RESPONSE FROM PYTHON API"
        );

      }

      // ============================
      // TIMEOUT
      // ============================

      if (
        error.code === "ECONNABORTED"
      ) {

        return res.status(500).json({
          success: false,
          message:
            "Server is waking up. Please try again in few seconds.",
        });

      }

      // ============================
      // FINAL ERROR
      // ============================

      res.status(500).json({
        success: false,
        message:
          error?.response?.data?.message ||
          error.message ||
          "Internal Server Error",
      });

    }

  }
);

// ============================
// GET ALL PERSONS
// ============================

router.get("/", async (req, res) => {

  try {

    const data = await Person.find();

    res.json(data);

  } catch (error) {

    res.status(500).json({
      success: false,
      message: error.message,
    });

  }

});

module.exports = router;