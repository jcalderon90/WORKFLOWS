const fs = require('fs');
const path = require('path');

const kbPath = path.join(__dirname, '../KBs/KB PPOL.json');
const workflowPath = path.join(__dirname, '../Agente Unificado/Vectorizar los KBs.json');

try {
  // 1. Read the correct PPOL KB chunks
  const kbData = JSON.parse(fs.readFileSync(kbPath, 'utf8'));
  console.log(`Successfully read ${kbData.length} chunks from KB PPOL.json`);

  // 2. Read the workflow JSON
  const workflow = JSON.parse(fs.readFileSync(workflowPath, 'utf8'));

  // 3. Find the "LISTA de CHUNKS" node
  const chunksNode = workflow.nodes.find(node => node.name === 'LISTA de CHUNKS');
  if (!chunksNode) {
    throw new Error('Could not find the "LISTA de CHUNKS" node in the workflow file.');
  }

  // 4. Update the "value" property in assignments
  const assignment = chunksNode.parameters.assignments.assignments.find(a => a.name === 'chunks');
  if (!assignment) {
    throw new Error('Could not find the "chunks" assignment in the node.');
  }

  // Set the value to the stringified version of the KB array, prefixed with '=' for n8n expressions
  assignment.value = '=' + JSON.stringify(kbData, null, 2);

  // 5. Write the updated workflow back to disk
  fs.writeFileSync(workflowPath, JSON.stringify(workflow, null, 2), 'utf8');
  console.log('Successfully updated "Vectorizar los KBs.json" with the official KB PPOL.json chunks!');
} catch (error) {
  console.error('Error updating vectorizer workflow:', error.message);
  process.exit(1);
}
