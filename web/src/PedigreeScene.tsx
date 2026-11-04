import { Environment, Float, Html, RoundedBox } from "@react-three/drei";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { people, segments, type Person3D, type Segment3D } from "./pedigree";

function Connection({ from, to }: Segment3D) {
  const { midpoint, quaternion, length } = useMemo(() => {
    const start = new THREE.Vector3(...from);
    const end = new THREE.Vector3(...to);
    const direction = end.clone().sub(start);
    return {
      midpoint: start.clone().add(end).multiplyScalar(0.5),
      quaternion: new THREE.Quaternion().setFromUnitVectors(
        new THREE.Vector3(0, 1, 0),
        direction.clone().normalize()
      ),
      length: direction.length()
    };
  }, [from, to]);

  return (
    <mesh position={midpoint} quaternion={quaternion} castShadow>
      <cylinderGeometry args={[0.035, 0.035, length, 18]} />
      <meshStandardMaterial color="#879197" metalness={0.86} roughness={0.28} />
    </mesh>
  );
}

function PersonNode({ person, selected, onSelect }: {
  person: Person3D;
  selected: boolean;
  onSelect: (person: Person3D) => void;
}) {
  const [hovered, setHovered] = useState(false);
  const material = (
    <meshPhysicalMaterial
      color={person.affected ? "#b95f43" : hovered || selected ? "#8cbec1" : "#718084"}
      transmission={person.affected ? 0.12 : 0.72}
      thickness={0.8}
      roughness={person.affected ? 0.38 : 0.2}
      metalness={person.affected ? 0.25 : 0.05}
      clearcoat={0.8}
      clearcoatRoughness={0.18}
      transparent
      opacity={0.96}
    />
  );

  const interaction = {
    onClick: (event: { stopPropagation: () => void }) => {
      event.stopPropagation();
      onSelect(person);
    },
    onPointerOver: (event: { stopPropagation: () => void }) => {
      event.stopPropagation();
      setHovered(true);
      document.body.style.cursor = "pointer";
    },
    onPointerOut: () => {
      setHovered(false);
      document.body.style.cursor = "default";
    }
  };

  return (
    <group position={person.position}>
      {person.shape === "square" && (
        <RoundedBox args={[0.66, 0.66, 0.22]} radius={0.07} smoothness={4} {...interaction}>
          {material}
        </RoundedBox>
      )}
      {person.shape === "circle" && (
        <mesh rotation={[Math.PI / 2, 0, 0]} {...interaction}>
          <cylinderGeometry args={[0.36, 0.36, 0.22, 48]} />
          {material}
        </mesh>
      )}
      {person.shape === "diamond" && (
        <RoundedBox
          args={[0.55, 0.55, 0.2]}
          radius={0.04}
          rotation={[0, 0, Math.PI / 4]}
          {...interaction}
        >
          {material}
        </RoundedBox>
      )}
      <Html center position={[0, -0.58, 0]} distanceFactor={8}>
        <span className="node-label">{person.id}</span>
      </Html>
      {(hovered || selected) && (
        <Html position={[0.5, 0.28, 0.15]} distanceFactor={7.5} zIndexRange={[20, 0]}>
          <div className="node-inspector">
            <strong>{person.id}</strong>
            <span>{person.label}</span>
          </div>
        </Html>
      )}
    </group>
  );
}

function GenerationPlane({ y, width, depth }: { y: number; width: number; depth: number }) {
  return (
    <mesh position={[-0.25, y - 0.32, depth]} receiveShadow>
      <boxGeometry args={[width, 0.055, 2.35]} />
      <meshPhysicalMaterial
        color="#31545a"
        transmission={0.8}
        thickness={0.45}
        roughness={0.3}
        transparent
        opacity={0.19}
      />
    </mesh>
  );
}

function CameraRig({ reducedMotion }: { reducedMotion: boolean }) {
  const { camera, pointer } = useThree();
  useFrame((state, delta) => {
    if (reducedMotion) return;
    const targetX = 0.55 + pointer.x * 0.42;
    const targetY = 1.25 + pointer.y * 0.24;
    camera.position.x = THREE.MathUtils.damp(camera.position.x, targetX, 3, delta);
    camera.position.y = THREE.MathUtils.damp(camera.position.y, targetY, 3, delta);
    camera.lookAt(-0.25, 0, 0);
    state.scene.rotation.y = THREE.MathUtils.damp(
      state.scene.rotation.y,
      pointer.x * 0.025,
      2.5,
      delta
    );
  });
  return null;
}

function Sculpture({ reducedMotion }: { reducedMotion: boolean }) {
  const group = useRef<THREE.Group>(null);
  const [selected, setSelected] = useState<Person3D | null>(null);
  useFrame((state) => {
    if (!group.current || reducedMotion) return;
    group.current.position.y = Math.sin(state.clock.elapsedTime * 0.45) * 0.035;
  });

  return (
    <Float speed={reducedMotion ? 0 : 0.35} rotationIntensity={0.03} floatIntensity={0.08}>
      <group ref={group} rotation={[-0.04, -0.14, 0]} onPointerMissed={() => setSelected(null)}>
        <GenerationPlane y={2.15} width={7.8} depth={-1.25} />
        <GenerationPlane y={0.05} width={7.2} depth={-0.58} />
        <GenerationPlane y={-2.1} width={5.4} depth={0.15} />
        {segments.map((segment, index) => (
          <Connection key={index} {...segment} />
        ))}
        {people.map((person) => (
          <PersonNode
            key={person.id}
            person={person}
            selected={selected?.id === person.id}
            onSelect={setSelected}
          />
        ))}
      </group>
    </Float>
  );
}

export function PedigreeScene({ reducedMotion }: { reducedMotion: boolean }) {
  return (
    <div className="scene" aria-label="Heredograma tridimensional interativo">
      <Canvas
        shadows
        dpr={[1, 1.75]}
        camera={{ position: [0.55, 1.25, 9.8], fov: 40, near: 0.1, far: 100 }}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      >
        <color attach="background" args={["#090e11"]} />
        <fog attach="fog" args={["#090e11", 10, 17]} />
        <ambientLight intensity={0.65} />
        <directionalLight
          position={[-4, 6, 7]}
          intensity={4.2}
          color="#e9ded0"
          castShadow
          shadow-mapSize={[1024, 1024]}
        />
        <pointLight position={[3, -2.5, 4]} intensity={11} color="#b45f40" distance={8} />
        <spotLight position={[4, 5, 1]} intensity={7} color="#6cabad" angle={0.5} penumbra={1} />
        <Sculpture reducedMotion={reducedMotion} />
        <CameraRig reducedMotion={reducedMotion} />
        <Environment preset="warehouse" environmentIntensity={0.28} />
      </Canvas>
    </div>
  );
}
