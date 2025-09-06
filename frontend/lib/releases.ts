import yaml from 'js-yaml';
import fs from 'fs';
import path from 'path';

interface Release {
  title: string;
  date: string;
  content: string;
}

interface ReleasesData {
  currentVersion: number;
  releases: Record<string, Release>;
}

const releasesPath = path.join(process.cwd(), 'data', 'releases.yaml');
const releasesYaml = fs.readFileSync(releasesPath, 'utf8');
const releases = yaml.load(releasesYaml) as ReleasesData;

export default releases;