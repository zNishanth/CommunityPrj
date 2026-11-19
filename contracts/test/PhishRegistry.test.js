const { expect } = require("chai");
const { ethers } = require("hardhat");
const { keccak256, toUtf8Bytes } = ethers;

describe("PhishRegistry", function () {
  let registry, owner, reporter, stranger;

  const PHISH_URL = "https://evil-login.secure-bank.phish.com/auth";
  const urlHash = keccak256(toUtf8Bytes(PHISH_URL));

  beforeEach(async () => {
    [owner, reporter, stranger] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("PhishRegistry");
    registry = await Factory.deploy();
    await registry.waitForDeployment();
  });

  it("owner can authorise a reporter", async () => {
    await registry.authoriseReporter(reporter.address);
    expect(await registry.authorisedReporters(reporter.address)).to.be.true;
  });

  it("authorised reporter can submit a phishing URL hash", async () => {
    await registry.authoriseReporter(reporter.address);
    await expect(registry.connect(reporter).reportPhishing(urlHash))
      .to.emit(registry, "PhishingReported")
      .withArgs(urlHash, reporter.address, await ethers.provider.getBlock("latest").then(b => b.timestamp + 1), 1);
    expect(await registry.isPhishing(urlHash)).to.be.true;
  });

  it("stranger cannot submit", async () => {
    await expect(registry.connect(stranger).reportPhishing(urlHash)).to.be.revertedWith(
      "Not authorised reporter"
    );
  });

  it("reputation score increases on multiple reporters", async () => {
    await registry.authoriseReporter(reporter.address);
    await registry.reportPhishing(urlHash);          // owner
    await registry.connect(reporter).reportPhishing(urlHash);
    const rec = await registry.getRecord(urlHash);
    expect(rec.score).to.equal(2n);
  });

  it("totalRecords returns correct count", async () => {
    await registry.reportPhishing(urlHash);
    expect(await registry.totalRecords()).to.equal(1n);
  });
});
