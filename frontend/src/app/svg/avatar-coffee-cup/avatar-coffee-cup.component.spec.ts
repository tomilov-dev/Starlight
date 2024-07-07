import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AvatarCoffeeCupComponent } from './avatar-coffee-cup.component';

describe('AvatarCoffeeCupComponent', () => {
  let component: AvatarCoffeeCupComponent;
  let fixture: ComponentFixture<AvatarCoffeeCupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AvatarCoffeeCupComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(AvatarCoffeeCupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
