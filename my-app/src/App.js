import React, { useState, useRef } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Paper,
  Typography,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import ReactMarkdown from "react-markdown";

function App() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      while (true) {
      const { done, value } = await reader.read();
      if (done){
        setLoading(false)
        break;
      }
      const chunk = decoder.decode(value, { stream: true });
      setResponse((prev) => prev + chunk);
    }
    } catch (error) {
      console.error("Error uploading file:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ padding: 3, maxWidth: 600, margin: "auto" }}>
      <Paper
        variant="outlined"
        sx={{
          padding: 3,
          textAlign: "center",
          cursor: "copy",
        }}
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
        <CloudUploadIcon />
        <Typography>
          {file
            ? `Selected File: ${file.name}`
            : "Drag & drop or click to select a file"}
        </Typography>
      </Paper>

      <Button
        variant="contained"
        color="primary"
        sx={{ marginTop: 2 }}
        onClick={handleUpload}
        disabled={loading}
      >
        {loading ? <CircularProgress color="inherit" /> : "Upload"}
      </Button>

      {response && (
        <Box sx={{ marginTop: 3 }}>
          <ReactMarkdown>{response}</ReactMarkdown>
        </Box>
      )}
    </Box>
  );
}

export default App;
