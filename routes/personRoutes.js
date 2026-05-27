const express = require("express");
const multer = require("multer");
const cloudinary = require("cloudinary").v2;
const { CloudinaryStorage } = require("multer-storage-cloudinary");
const Person = require("../models/person");
const axios = require("axios");

const router = express.Router();

// =====================================
// CLOUDINARY CONFIG
// =====================================

cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
});

// =====================================
// AXIOS INSTANCE
// =====================================

const axiosInstance = axios.create({
  timeout: 60000,
});

// =====================================
// CLOUDINARY STORAGE
// =====================================

const storage = new CloudinaryStorage({
  cloudinary,
  params: {
    folder: "mern_profiles",
    allowed_formats: ["jpg", "jpeg", "png"],
  },
});

const upload = multer({
  storage,
});

// =====================================
// CREATE PERSON
// =====================================

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

      console.log("===== API HIT =====");

      // =====================================
      // VALIDATION
      // =====================================

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

      // =====================================
      // IMAGE PATHS
      // =====================================

      const profileImage =
        req.files.photo[0].path;

      const idCardImage =
        req.files.idCardPhoto[0].path;

      console.log("PROFILE IMAGE:");
      console.log(profileImage);

      console.log("ID CARD IMAGE:");
      console.log(idCardImage);

      console.log("PYTHON API URL:");
      console.log(process.env.PYTHON_API_URL);

      // =====================================
      // DETECT API
      // =====================================

      const detectRes =
        await axiosInstance.post(
          `${process.env.PYTHON_API_URL}/detect`,
          {
            image_url: profileImage,
          }
        );

      console.log("DETECTION RESPONSE:");
      console.log(detectRes.data);

      // =====================================
      // IDCARD VALIDATION
      // =====================================

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

      // =====================================
      // OCR API
      // =====================================

      let ocrData = {};
      let rawText = [];

      try {

        const ocrRes =
          await axiosInstance.post(
            `${process.env.PYTHON_API_URL}/ocr`,
            {
              image_url: idCardImage,
            }
          );

        console.log("OCR RESPONSE:");
        console.log(ocrRes.data);

        ocrData =
          ocrRes?.data?.data || {};

        rawText =
          ocrRes?.data?.raw_text || [];

      } catch (ocrError) {

        console.log("===== OCR ERROR =====");

        console.log(ocrError.message);

        if (ocrError.response) {

          console.log("OCR STATUS:");
          console.log(
            ocrError.response.status
          );

          console.log("OCR DATA:");
          console.log(
            ocrError.response.data
          );

        }

      }

      // =====================================
      // SAVE DATABASE
      // =====================================

      const newPerson = new Person({

        name: req.body.name,

        dob: req.body.dob,

        department:
          req.body.department,

        phone: req.body.phone,

        email: req.body.email,

        location:
          req.body.location,

        photo: profileImage,

        idCardImage:
          idCardImage,

        idCard:
          detectRes.data
            .id_card_detected,

        ocrData: ocrData,

        rawText: rawText,

      });

      await newPerson.save();

      // =====================================
      // SUCCESS RESPONSE
      // =====================================

      return res.json({

        success: true,

        message:
          "Profile saved successfully",

        data: newPerson,

      });

    } catch (error) {

      console.log(
        "===== FULL ERROR ====="
      );

      console.log(error);

      console.log("MESSAGE:");
      console.log(error.message);

      // =====================================
      // AXIOS ERROR
      // =====================================

      if (error.response) {

        console.log("STATUS:");
        console.log(
          error.response.status
        );

        console.log("DATA:");
        console.log(
          error.response.data
        );

      }

      // =====================================
      // TIMEOUT
      // =====================================

      if (
        error.code ===
        "ECONNABORTED"
      ) {

        return res.status(500).json({
          success: false,
          message:
            "Server timeout. Please try again.",
        });

      }

      // =====================================
      // FINAL ERROR
      // =====================================

      return res.status(500).json({

        success: false,

        message:
          error?.response?.data
            ?.message ||
          error.message ||
          "Internal Server Error",

      });

    }
  }
);

// =====================================
// GET ALL PERSONS
// =====================================

router.get("/", async (req, res) => {
  try {

    const data =
      await Person.find().sort({
        createdAt: -1,
      });

    res.json({
      success: true,
      data,
    });

  } catch (error) {

    res.status(500).json({
      success: false,
      message: error.message,
    });

  }
});

module.exports = router;