const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying PhishRegistry with account:", deployer.address);

  const PhishRegistry = await hre.ethers.getContractFactory("PhishRegistry");
  const contract = await PhishRegistry.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("PhishRegistry deployed to:", address);

  // Write ABI + address for backend
  const artifact = await hre.artifacts.readArtifact("PhishRegistry");
  const deployInfo = {
    address,
    abi: artifact.abi,
    network: hre.network.name,
    deployedAt: new Date().toISOString(),
  };

  const outPath = path.join(__dirname, "../PhishRegistry.json");
  fs.writeFileSync(outPath, JSON.stringify(deployInfo, null, 2));
  console.log("ABI + address written to", outPath);

  // Also write to backend location
  const backendOut = path.join(
    __dirname,
    "../../../backend/contracts/PhishRegistry.json"
  );
  fs.mkdirSync(path.dirname(backendOut), { recursive: true });
  fs.writeFileSync(backendOut, JSON.stringify(deployInfo, null, 2));
  console.log("Copied to backend at", backendOut);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
