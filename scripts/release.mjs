import { readFileSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';
import path from 'path';

const MANIFEST_PATH = path.join(process.cwd(), 'custom_components', 'luxpower_modbus', 'manifest.json');

const bumpType = process.argv[2];
if (!['patch', 'minor', 'major'].includes(bumpType)) {
  console.error('Error: Invalid version bump type. Use "patch", "minor", or "major".');
  process.exit(1);
}

try {
  // 1. Read and bump version in manifest.json
  console.log('Reading manifest.json...');
  const manifestRaw = readFileSync(MANIFEST_PATH, 'utf-8');
  const manifest = JSON.parse(manifestRaw);
  const currentVersion = manifest.version;

  let [major, minor, patch] = currentVersion.split('.').map(Number);
  if (bumpType === 'patch') {
    patch += 1;
  } else if (bumpType === 'minor') {
    minor += 1;
    patch = 0;
  } else if (bumpType === 'major') {
    major += 1;
    minor = 0;
    patch = 0;
  }
  const newVersion = `${major}.${minor}.${patch}`;
  manifest.version = newVersion;
  
  // Use 2 spaces for indentation to match Home Assistant standards
  writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2) + '\n');
  console.log(`Version bumped from ${currentVersion} to ${newVersion}`);

  // 2. Git commit, tag, and push
  const tagName = `v${newVersion}`;
  console.log('Committing and tagging...');
  execSync(`git add ${MANIFEST_PATH}`);
  execSync(`git commit -m "chore(release): version ${tagName}"`);
  execSync(`git tag ${tagName}`);
  console.log('Pushing to origin...');
  execSync('git push');
  execSync('git push --tags');

  // 3. Create GitHub Release
  console.log(`Creating GitHub release for ${tagName}...`);
  execSync(`gh release create ${tagName} --generate-notes`);

  console.log('\n✅ Release created successfully!');
  console.log(`Visit https://github.com/Andru/Luxpower-Modbus-RTU/releases/tag/${tagName} to see the new release.`);

} catch (error) {
  console.error('\n❌ An error occurred during the release process:');
  console.error(error.message);
  console.error('You may need to manually clean up the failed state (e.g., delete a local tag).');
  process.exit(1);
}
