const mongoose = require("mongoose");

const personSchema = new mongoose.Schema({
  name: String,
  dob: String,
   age: Number,
  department: String,
  phone: String,
  email: String,
  location: String,
  photo: String,

  idCard: Boolean,
  backgroundText: [String],

  ocrData: mongoose.Schema.Types.Mixed,

  rawText: [String]
});

module.exports = mongoose.model("Person", personSchema);