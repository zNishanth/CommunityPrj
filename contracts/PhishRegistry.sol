// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PhishRegistry
 * @dev Immutable on-chain registry of phishing URL hashes.
 *      Anyone can query. Only authorised reporters can submit.
 *      Hashes are keccak256 of the full URL encoded as bytes.
 */
contract PhishRegistry {

    // ----- Events ----------------------------------------------------------

    event PhishingReported(
        bytes32 indexed urlHash,
        address indexed reporter,
        uint256 timestamp,
        uint256 reputationScore
    );

    event ReporterAuthorised(address indexed reporter);
    event ReporterRevoked(address indexed reporter);

    // ----- State -----------------------------------------------------------

    address public owner;

    struct PhishRecord {
        address firstReporter;
        uint256 timestamp;
        uint256 reputationScore;   // number of independent reporters
        bool    confirmed;         // owner can confirm after review
    }

    mapping(bytes32 => PhishRecord)  public records;         // urlHash => record
    mapping(address => bool)         public authorisedReporters;
    mapping(bytes32 => mapping(address => bool)) public hasReported; // avoid double-reporting

    bytes32[] public allHashes;   // iteration support

    // ----- Constructor -----------------------------------------------------

    constructor() {
        owner = msg.sender;
        authorisedReporters[msg.sender] = true;
    }

    // ----- Modifiers -------------------------------------------------------

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyReporter() {
        require(authorisedReporters[msg.sender], "Not authorised reporter");
        _;
    }

    // ----- Admin -----------------------------------------------------------

    function authoriseReporter(address reporter) external onlyOwner {
        authorisedReporters[reporter] = true;
        emit ReporterAuthorised(reporter);
    }

    function revokeReporter(address reporter) external onlyOwner {
        authorisedReporters[reporter] = false;
        emit ReporterRevoked(reporter);
    }

    function confirmRecord(bytes32 urlHash) external onlyOwner {
        require(records[urlHash].timestamp != 0, "Record not found");
        records[urlHash].confirmed = true;
    }

    // ----- Core ------------------------------------------------------------

    /**
     * @notice Report a phishing URL by its keccak256 hash.
     * @dev The hash must equal keccak256(abi.encodePacked(url)) from the backend.
     */
    function reportPhishing(bytes32 urlHash) external onlyReporter {
        require(!hasReported[urlHash][msg.sender], "Already reported");

        hasReported[urlHash][msg.sender] = true;

        if (records[urlHash].timestamp == 0) {
            // First report
            records[urlHash] = PhishRecord({
                firstReporter:    msg.sender,
                timestamp:        block.timestamp,
                reputationScore:  1,
                confirmed:        false
            });
            allHashes.push(urlHash);
        } else {
            records[urlHash].reputationScore += 1;
        }

        emit PhishingReported(
            urlHash,
            msg.sender,
            block.timestamp,
            records[urlHash].reputationScore
        );
    }

    // ----- Queries ---------------------------------------------------------

    function isPhishing(bytes32 urlHash) external view returns (bool) {
        return records[urlHash].timestamp != 0;
    }

    function getRecord(bytes32 urlHash)
        external view
        returns (address firstReporter, uint256 timestamp, uint256 score, bool confirmed)
    {
        PhishRecord memory r = records[urlHash];
        return (r.firstReporter, r.timestamp, r.reputationScore, r.confirmed);
    }

    function totalRecords() external view returns (uint256) {
        return allHashes.length;
    }
}
