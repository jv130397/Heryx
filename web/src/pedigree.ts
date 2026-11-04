export type PersonShape = "square" | "circle" | "diamond";

export interface Person3D {
  id: string;
  label: string;
  shape: PersonShape;
  position: [number, number, number];
  affected?: boolean;
  proband?: boolean;
}

export interface Segment3D {
  from: [number, number, number];
  to: [number, number, number];
}

export const people: Person3D[] = [
  { id: "I-1", label: "Avô materno", shape: "square", position: [-3.5, 2.15, -0.45] },
  { id: "I-2", label: "Avó materna", shape: "circle", position: [-1.75, 2.15, -0.45] },
  { id: "I-3", label: "Avô paterno", shape: "square", position: [1.05, 2.15, -1.1] },
  { id: "I-4", label: "Avó paterna", shape: "circle", position: [2.8, 2.15, -1.1] },
  { id: "II-1", label: "Mãe", shape: "circle", position: [-1.9, 0.05, 0.05] },
  { id: "II-2", label: "Pai", shape: "square", position: [0.1, 0.05, -0.25] },
  { id: "II-3", label: "Tia paterna", shape: "circle", position: [2.0, 0.05, -0.75] },
  {
    id: "III-1",
    label: "Probando · avaliação clínica",
    shape: "square",
    position: [-0.85, -2.1, 0.7],
    affected: true,
    proband: true
  },
  { id: "III-2", label: "Irmão", shape: "diamond", position: [0.9, -2.1, 0.3] }
];

const z1 = -0.45;
const z2 = -0.25;
const z3 = 0.5;

export const segments: Segment3D[] = [
  { from: [-3.5, 2.15, z1], to: [-1.75, 2.15, z1] },
  { from: [-2.625, 2.15, z1], to: [-2.625, 0.75, z2] },
  { from: [-2.625, 0.75, z2], to: [-1.9, 0.75, z2] },
  { from: [-1.9, 0.75, z2], to: [-1.9, 0.05, 0.05] },
  { from: [1.05, 2.15, -1.1], to: [2.8, 2.15, -1.1] },
  { from: [1.925, 2.15, -1.1], to: [1.925, 0.75, -0.6] },
  { from: [0.1, 0.75, -0.4], to: [2.0, 0.75, -0.6] },
  { from: [0.1, 0.75, -0.4], to: [0.1, 0.05, -0.25] },
  { from: [2.0, 0.75, -0.6], to: [2.0, 0.05, -0.75] },
  { from: [-1.9, 0.05, z2], to: [0.1, 0.05, z2] },
  { from: [-0.9, 0.05, z2], to: [-0.9, -1.35, z3] },
  { from: [-0.85, -1.35, z3], to: [0.9, -1.35, 0.4] },
  { from: [-0.85, -1.35, z3], to: [-0.85, -2.1, 0.7] },
  { from: [0.9, -1.35, 0.4], to: [0.9, -2.1, 0.3] }
];
