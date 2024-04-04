import React, { Fragment, useState } from "react";
import axios from "axios";
import "./App.css";
import { FaSearch } from "react-icons/fa";
import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import "bootstrap/dist/css/bootstrap.min.css";
// import Results from "./Components/Results";

function SearchBar({ onSearch }) {
  const [searchTerm, setSearchTerm] = useState("");

  const handleInputChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSearch(searchTerm);
  };

  return (
    <form onSubmit={handleSubmit} className="search-container">
      <input
        type="text"
        placeholder="Search..."
        value={searchTerm}
        onChange={handleInputChange}
        className="search-input"
      />
      <button type="submit" className="search-icon">
        <FaSearch />
      </button>
    </form>
  );
}

function SearchResult({ results }) {
  return (
    <div>
      <h2 className=" mt-4">Search Results</h2>
      <ul>
        {Array.isArray(results) ? (
          <Fragment>
            {results.length !== 0 && <h4>Found {results.length} items.</h4>}
            {results.map((result) => (
              <li className="result-list" key={result.id}>
                {result.title}
              </li>
            ))}
          </Fragment>
        ) : (
          <li>No results found</li>
        )}
      </ul>
    </div>
  );
}

function App() {
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = (searchTerm) => {
    let config = {
      method: "get",
      maxBodyLength: Infinity,
      url: `https://dummyjson.com/posts/search?q=${searchTerm}`,
      headers: {},
    };

    searchTerm !== "" &&
      axios
        .request(config)
        .then((response) => {
          console.log(JSON.stringify(response.data.posts));
          setSearchResults(response.data.posts);
        })
        .catch((error) => {
          console.log(error);
        });
  };

  return (
    <Fragment>
      <Navbar bg="dark" data-bs-theme="dark">
        <Container>
          <Navbar.Brand href="#home">Text Analyser</Navbar.Brand>
          <Nav className="me-auto">
            <Nav.Link href="#home">Home</Nav.Link>
            <Nav.Link href="#features">Features</Nav.Link>
            <Nav.Link href="#help">Help</Nav.Link>
          </Nav>
        </Container>
      </Navbar>
      <h1 className=" mt-4">Text Analyser </h1>
      <SearchBar onSearch={handleSearch} />
      <SearchResult results={searchResults} />
    </Fragment>
  );
}

export default App;
