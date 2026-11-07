import { describe,expect,it } from "vitest";
import { validateClinicalProject } from "./clinicalValidation";

describe("clinical project validation",()=>{
  it("detects duplicate probands and invalid HPO identifiers",()=>{
    const issues=validateClinicalProject({schema_version:"0.4.0",individuals:[{id:"1",label:"I-1",proband:true,hpo_terms:[{id:"invalid"}]},{id:"2",label:"I-2",proband:true}]});
    expect(issues.map(issue=>issue.code)).toEqual(expect.arrayContaining(["MULTIPLE_PROBANDS","INVALID_HPO"]));
  });
  it("accepts a minimal consistent pedigree",()=>{
    expect(validateClinicalProject({schema_version:"0.4.0",individuals:[{id:"1",label:"I-1",gender_identity:"unknown",proband:true,hpo_terms:[{id:"HP:0001250"}]}]})).toEqual([]);
  });
});
