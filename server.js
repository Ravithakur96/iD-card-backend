const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const dotenv = require("dotenv");

dotenv.config();

const app = express();
const cors = require("cors");

app.use(cors());
app.use(express.json());


const personRoutes = require("./routes/personRoutes");

app.use("/api/persons", personRoutes);

const locationRoutes = require("./routes/locationRoutes");

app.use("/api/location", locationRoutes);

mongoose.connect(process.env.MONGO_URI)
.then(() => {
  console.log("MongoDB Connected");
})
.catch((err) => {
  console.log("Mongo Error:", err);
});

app.get("/", (req, res) => {
  res.send("API Running");
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});