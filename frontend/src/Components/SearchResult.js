import React, { Fragment, useState } from "react";
import axios from "axios";
import {
  Spinner,
  Card,
  Offcanvas,
  Col,
  Row,
  Button,
  Form,
  Pagination,
  Container,
} from "react-bootstrap";
import { FaSearch } from "react-icons/fa";
import { Link } from "react-router-dom";

function SearchResult() {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showOffCanvas, setShowOffCanvas] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);
  const [selectedCards, setSelectedCards] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [method, setMethod] = useState("relevancy");
  const [dateOrder, setDateOrder] = useState("DESC");
  const [authorFilter, setAuthorFilter] = useState("");

  const handleInputChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleSearch = (event) => {
    event.preventDefault();
    if (searchTerm.trim() !== "") {
      let data = JSON.stringify({
        query: searchTerm,
        author: authorFilter,
        method: method,
        date_order: dateOrder,
      });

      let config = {
        method: "post",
        maxBodyLength: Infinity,
        url: "http://localhost:5000/filterselect",
        headers: {
          "Content-Type": "application/json",
        },
        data: data,
      };

      setIsLoading(true);
      axios
        .request(config)
        .then((response) => {
          let results = response.data;
          setSearchResults(results);
        })
        .catch((error) => {
          console.log(error);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  };

  const handleCardClick = (result) => {
    setSelectedResult(result);
    setShowOffCanvas(true);
  };

  const handleCloseOffCanvas = () => {
    setShowOffCanvas(false);
  };

  const handleCheckboxChange = (event, result) => {
    if (event.target.checked) {
      setSelectedCards([...selectedCards, result]);
    } else {
      setSelectedCards(selectedCards.filter((card) => card.DOI !== result.DOI));
    }
  };

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const handleMethodChange = (event) => {
    setMethod(event.target.value);
  };

  const handleDateOrderChange = (event) => {
    setDateOrder(event.target.value);
  };

  const handleAuthorFilterChange = (event) => {
    setAuthorFilter(event.target.value);
  };

  const indexOfLastCard = currentPage * 8;
  const indexOfFirstCard = indexOfLastCard - 8;
  const currentCards = searchResults.slice(indexOfFirstCard, indexOfLastCard);

  const renderCards = currentCards.map((result, index) => (
    <Card
      key={result.return_id}
      className="mb-1 flex-row"
      style={{ cursor: "pointer" }}
    >
      <Form.Check
        type="checkbox"
        onChange={(event) => handleCheckboxChange(event, result)}
        key={result.return_id}
        className=" mt-3 px-3"
      />
      <div className="row">
        <Card.Body onClick={() => handleCardClick(result)} className=" p-2">
          <p className=" m-1" style={{ fontSize: 16 }}>
            {result.title}
          </p>
          <footer className="text-muted" style={{ fontSize: 12 }}>
            Citation :{" "}
            {result.citationCount
              ? result.citationCount
              : result.cited_by_count
              ? result.cited_by_count
              : 0}
            <span> Date : {result.date ? result.date : "None"}</span>
          </footer>
        </Card.Body>
      </div>
    </Card>
  ));

  const items = [];
  for (
    let number = 1;
    number <= Math.ceil(searchResults.length / 8);
    number++
  ) {
    items.push(
      <Pagination.Item
        key={number}
        active={number === currentPage}
        onClick={() => handlePageChange(number)}
      >
        {number}
      </Pagination.Item>
    );
  }

  const paginationBasic = (
    <div className="text-center mt-3">
      <Pagination>{items}</Pagination>
    </div>
  );

  return (
    <Fragment>
      <h1 className="mt-4 text-center">Systematic Scholar</h1>
      <Container>
        <form onSubmit={handleSearch} className="search-container">
          <div className="input-group">
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={handleInputChange}
              className="form-control"
              style={{
                height: "45px",
                borderRadius: "20px",
              }}
            />
            <div className="input-group-append">
              <button
                type="submit"
                className="search-icon"
                style={{
                  borderRadius: "20px",
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                <FaSearch style={{ color: "#555", fontSize: "1.2em" }} />
              </button>
            </div>
          </div>
        </form>
      </Container>
      {isLoading ? (
        <div className=" text-center mt-4">
          <Spinner animation="border" role="status">
            <span className="sr-only"></span>
          </Spinner>
        </div>
      ) : (
        <Container fluid>
          {renderCards.length > 0 ? (
            <Fragment>
              <div className=" mt-3">
                <Link
                  as={Button}
                  to="/location"
                  state={{ selectedCards: selectedCards }}
                  className={`btn btn-${
                    selectedCards.length !== 0 ? "primary" : "secondary"
                  }`}
                  style={{
                    cursor:
                      selectedCards.length === 0 ? "not-allowed" : "pointer",
                  }}
                  disabled={selectedCards.length === 0}
                >
                  Show Map
                </Link>
              </div>
              <Row className="flex-row mt-3">
                <Col xs={7}>{renderCards}</Col>
                <Col>
                  <Card className="p-3">
                    <h2>Filters</h2>
                    <div style={{ fontSize: 14 }}>
                      <Form.Group className=" mb-3">
                        <Form.Label>Order by:</Form.Label>
                        <div>
                          <Form.Check
                            inline
                            label="Relevancy"
                            type="radio"
                            value="relevancy"
                            checked={method === "relevancy"}
                            onChange={handleMethodChange}
                          />
                          <Form.Check
                            inline
                            label="Citation"
                            type="radio"
                            value="citation"
                            checked={method === "citation"}
                            onChange={handleMethodChange}
                          />
                          <Form.Check
                            inline
                            label="Filter by author"
                            type="radio"
                            value="FilterByAuthor"
                            checked={method === "FilterByAuthor"}
                            onChange={handleMethodChange}
                          />
                        </div>
                      </Form.Group>
                      <Form.Group className=" mb-3">
                        <Form.Label>Date Order:</Form.Label>
                        <div>
                          <Form.Check
                            inline
                            label="Descending"
                            type="radio"
                            value="DESC"
                            checked={dateOrder === "DESC"}
                            onChange={handleDateOrderChange}
                          />
                          <Form.Check
                            inline
                            label="Ascending"
                            type="radio"
                            value="ASC"
                            checked={dateOrder === "ASC"}
                            onChange={handleDateOrderChange}
                          />
                        </div>
                      </Form.Group>
                      <Form.Group className=" mb-lg-5">
                        <Form.Label>Author:</Form.Label>
                        <Form.Control
                          type="text"
                          placeholder="Search by author"
                          value={authorFilter}
                          onChange={handleAuthorFilterChange}
                        />
                      </Form.Group>
                    </div>
                  </Card>
                </Col>
              </Row>
              {paginationBasic}
            </Fragment>
          ) : (
            ""
          )}
        </Container>
      )}
      <Offcanvas
        show={showOffCanvas}
        onHide={handleCloseOffCanvas}
        placement="end"
        style={{ width: "43%" }}
      >
        <Offcanvas.Header closeButton>
          <Offcanvas.Title>{selectedResult?.title}</Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body>
          <p>
            <b>DOI</b>: {selectedResult?.DOI}
          </p>
          <p>
            <b>Abstract</b>:{" "}
            <span className=" justify-content-evenly">
              {selectedResult?.abstract}
            </span>
          </p>
          <p>
            <b>Citation Count</b>:{" "}
            {selectedResult?.citationCount
              ? selectedResult?.citationCount
              : selectedResult?.cited_by_count
              ? selectedResult?.cited_by_count
              : 0}
          </p>
          <p>
            <b>Date</b>: {selectedResult?.date ? selectedResult?.date : "None"}
          </p>
          <p>
            <b> Source</b>:{" "}
            {selectedResult?.source ? selectedResult?.source : "None"}
          </p>
          <p>
            <b>Authors</b>:
          </p>
          <ul>
            {selectedResult?.authors.map((author, index) => (
              <li key={index}>{author.name}</li>
            ))}
          </ul>
        </Offcanvas.Body>
      </Offcanvas>
    </Fragment>
  );
}

export default SearchResult;
