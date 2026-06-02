const mongoose = require("mongoose");

const personSchema = new mongoose.Schema({
  name: String,
  dob: String,
  department: String,
  phone: String,
  email: String,
  location: String,
  photo: String,

  idCard: Boolean,

  ocrData: mongoose.Schema.Types.Mixed,

  rawText: [String]
});

module.exports = mongoose.model("Person", personSchema);