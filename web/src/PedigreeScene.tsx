import { Environment, Float, Sparkles, useTexture } from "@react-three/drei";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";

type Point = [number, number, number];

function Tube({ from, to, color = "#4ad8ff", radius = .018 }: { from: Point; to: Point; color?: string; radius?: number }) {
  const values = useMemo(() => {
    const start = new THREE.Vector3(...from); const end = new THREE.Vector3(...to); const direction = end.clone().sub(start);
    return { midpoint: start.clone().add(end).multiplyScalar(.5), length: direction.length(), quaternion: new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize()) };
  }, [from, to]);
  return <mesh position={values.midpoint} quaternion={values.quaternion}><cylinderGeometry args={[radius, radius, values.length, 10]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={3} toneMapped={false} /></mesh>;
}

function Hologram({ introPhase }: { introPhase: number }) {
  const group = useRef<THREE.Group>(null);
  useFrame((state, delta) => { if (group.current) { group.current.rotation.y = Math.sin(state.clock.elapsedTime * .22) * .08; const target = introPhase >= 2 ? 1 : .001; const scale = THREE.MathUtils.damp(group.current.scale.x, target, 3.5, delta); group.current.scale.setScalar(scale); } });
  const nodes: Array<[number, number, number, "square" | "circle"]> = [[-1.2,.8,0,"square"],[0,.8,0,"circle"],[1.25,.8,0,"square"],[-.65,-.2,0,"circle"],[.65,-.2,0,"square"],[0,-1.15,0,"circle"]];
  const links: Array<[Point,Point]> = [[[-1.2,.8,0],[0,.8,0]],[[.6,.8,0],[1.25,.8,0]],[[-.6,.8,0],[-.6,-.2,0]],[[.6,.8,0],[.6,-.2,0]],[[-.65,-.2,0],[.65,-.2,0]],[[0,-.2,0],[0,-1.15,0]]];
  return <Float speed={.7} floatIntensity={.12} rotationIntensity={.02}><group ref={group} position={[2.45,2.25,-1.35]} rotation={[-.08,-.2,0]}>
    {links.map(([from,to], index) => <Tube key={index} from={from} to={to} />)}
    {nodes.map(([x,y,z,shape], index) => <mesh key={index} position={[x,y,z]} rotation={shape === "circle" ? [Math.PI/2,0,0] : [0,0,0]}>{shape === "circle" ? <cylinderGeometry args={[.18,.18,.06,32]} /> : <boxGeometry args={[.34,.34,.07]} />}<meshPhysicalMaterial color="#aaf3ff" emissive="#2fd4ff" emissiveIntensity={2.8} transparent opacity={.78} transmission={.35} /></mesh>)}
    <pointLight color="#49dfff" intensity={5} distance={5} />
  </group></Float>;
}

function Avatar({ introPhase }: { introPhase: number }) {
  const source = useTexture("/assets/joao-vitor-game-avatar.png");
  const texture = useMemo(() => source.clone(), [source]);
  const avatar = useRef<THREE.Group>(null);
  useEffect(() => { texture.needsUpdate = true; texture.repeat.set(1 / 3, 1 / 2); texture.offset.set(introPhase === 1 || introPhase === 2 ? 1 / 3 : 0, 1 / 2); texture.colorSpace = THREE.SRGBColorSpace; texture.magFilter = THREE.NearestFilter; }, [texture, introPhase]);
  useFrame((state) => { if (avatar.current) avatar.current.position.y = Math.sin(state.clock.elapsedTime * 1.25) * .035; });
  return <group ref={avatar} position={[-.35,.2,.7]} rotation={[0,.12,0]}>
    <mesh castShadow><planeGeometry args={[2.65,2.65]} /><meshBasicMaterial map={texture} transparent toneMapped={false} /></mesh>
    <pointLight position={[0,1,.8]} color="#17d5ec" intensity={1.5} distance={4} />
  </group>;
}

function Observatory({ introPhase }: { introPhase: number }) {
  return <group>
    <mesh position={[0,-1.25,0]} receiveShadow><cylinderGeometry args={[5.8,6.4,.42,8]} /><meshStandardMaterial color="#101b24" metalness={.72} roughness={.42} /></mesh>
    <mesh position={[0,-1.02,0]} rotation={[-Math.PI/2,0,0]}><ringGeometry args={[3.9,4.02,64]} /><meshBasicMaterial color="#20c7ee" toneMapped={false} /></mesh>
    <mesh position={[0,-1,0]} rotation={[-Math.PI/2,0,0]} receiveShadow><circleGeometry args={[5.65,64]} /><meshStandardMaterial color="#07121a" metalness={.5} roughness={.5} /></mesh>
    {[0,1,2,3,4,5,6].map((i) => <mesh key={i} position={[-6 + i * 2,-.2,-4.2 - Math.abs(3-i) * .25]}><boxGeometry args={[.12,2.3,.12]} /><meshStandardMaterial color="#1e4351" emissive="#0b5368" emissiveIntensity={1.1} /></mesh>)}
    <mesh position={[2.45,.05,-1.35]} castShadow><cylinderGeometry args={[1.35,1.6,.36,32]} /><meshStandardMaterial color="#122837" metalness={.75} roughness={.25} /></mesh>
    <mesh position={[2.45,.25,-1.35]}><cylinderGeometry args={[1.05,1.25,.05,32]} /><meshStandardMaterial color="#1bd0f4" emissive="#0b9fbd" emissiveIntensity={2} /></mesh>
    <Hologram introPhase={introPhase} /><Avatar introPhase={introPhase} /><Sparkles count={55} scale={[12,6,8]} size={1.2} speed={.15} color="#68ddf5" opacity={.45} />
  </group>;
}

function CameraRig({ reducedMotion, entered }: { reducedMotion: boolean; entered: boolean }) {
  const { camera, pointer } = useThree();
  useFrame((_, delta) => {
    const targetX = reducedMotion ? 0 : pointer.x * .45; const targetY = reducedMotion ? 1.05 : 1.05 + pointer.y * .22;
    camera.position.x = THREE.MathUtils.damp(camera.position.x,targetX,2.5,delta); camera.position.y = THREE.MathUtils.damp(camera.position.y,targetY,2.5,delta); camera.position.z = THREE.MathUtils.damp(camera.position.z,entered ? 7.4 : 9.4,1.4,delta); camera.lookAt(0,.55,-.5);
  });
  return null;
}

export function PedigreeScene({ reducedMotion, entered, introPhase }: { reducedMotion: boolean; entered: boolean; introPhase: number }) {
  return <div className="scene" aria-label="Observatório genômico tridimensional interativo"><Canvas shadows dpr={[1,1.75]} camera={{ position:[0,1.05,9.4],fov:43,near:.1,far:100 }} gl={{ antialias:true,alpha:true,powerPreference:"high-performance" }}>
    <color attach="background" args={["#03090f"]} /><fog attach="fog" args={["#03090f",8,21]} /><ambientLight intensity={.42} />
    <directionalLight position={[-3,7,5]} intensity={3.4} color="#d6f6ff" castShadow shadow-mapSize={[1024,1024]} /><spotLight position={[2,7,1]} intensity={8} color="#2bdcff" angle={.42} penumbra={1} castShadow /><pointLight position={[-4,1,2]} intensity={5} color="#4656ff" distance={9} />
    <Observatory introPhase={introPhase} /><CameraRig reducedMotion={reducedMotion} entered={entered} /><Environment preset="night" environmentIntensity={.22} />
  </Canvas></div>;
}
