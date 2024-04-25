import React, { Fragment } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import SearchResult from "./Components/SearchResult";
import Location from "./Components/Location";
import { Navbar, Nav, Container } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

function App() {
  return (
    <Router>
      <Fragment>
        <Navbar bg="dark" data-bs-theme="dark">
          <Container>
            <Navbar.Brand as={Link} to="/">
              Systematic Scholar
            </Navbar.Brand>
            <Nav className="justify-content-end">
              <Nav.Link as={Link} to="/">
                Features
              </Nav.Link>
              <Nav.Link as={Link} to="/">
                Help
              </Nav.Link>
            </Nav>
          </Container>
        </Navbar>

        <Routes>
          <Route path="/" element={<SearchResult />} />
          <Route path="/location" element={<Location />} />
        </Routes>
      </Fragment>
    </Router>
  );
}
export default App;
