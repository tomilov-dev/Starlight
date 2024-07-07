import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ItemPersonComponent } from './item-person.component';

describe('ItemPersonComponent', () => {
  let component: ItemPersonComponent;
  let fixture: ComponentFixture<ItemPersonComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ItemPersonComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ItemPersonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
