// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title PhishRegistry — on-chain phishing URL hash registry for catchPhish
contract PhishRegistry {
    struct Record {
        bytes32  urlHash;
        address  reporter;
        uint256  timestamp;
        uint32   reputation;   // number of confirmations
        bool     exists;
    }

    address public owner;
    mapping(bytes32 => Record) private _records;
    bytes32[] private _hashes;

    event Reported(bytes32 indexed urlHash, address indexed reporter, uint256 timestamp);
    event Confirmed(bytes32 indexed urlHash, address indexed confirmer, uint32 reputation);

    modifier onlyOwner() {
        require(msg.sender == owner, "PhishRegistry: not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /// @notice Report a URL hash as phishing.
    function reportPhishing(bytes32 urlHash) external {
        if (!_records[urlHash].exists) {
            _records[urlHash] = Record({
                urlHash:    urlHash,
                reporter:   msg.sender,
                timestamp:  block.timestamp,
                reputation: 1,
                exists:     true
            });
            _hashes.push(urlHash);
            emit Reported(urlHash, msg.sender, block.timestamp);
        } else {
            _records[urlHash].reputation += 1;
            emit Confirmed(urlHash, msg.sender, _records[urlHash].reputation);
        }
    }

    /// @notice Check whether a URL hash is registered as phishing.
    function isPhishing(bytes32 urlHash) external view returns (bool) {
        return _records[urlHash].exists;
    }

    /// @notice Return full record for a URL hash.
    function getRecord(bytes32 urlHash)
        external
        view
        returns (address reporter, uint256 timestamp, uint32 reputation, bool exists)
    {
        Record storage r = _records[urlHash];
        return (r.reporter, r.timestamp, r.reputation, r.exists);
    }

    /// @notice Total number of reported hashes.
    function totalReports() external view returns (uint256) {
        return _hashes.length;
    }

    /// @notice Owner can remove a false-positive entry.
    function removeRecord(bytes32 urlHash) external onlyOwner {
        delete _records[urlHash];
    }
}
